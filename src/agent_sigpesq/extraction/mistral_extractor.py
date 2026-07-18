"""
ProjectExtractor: turn a SIGPESQ project PDF into a validated `Projeto` JSON
using the Mistral API (OCR + chat in JSON mode).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from mistralai import Mistral

from .schema import Projeto, JSON_TEMPLATE

OCR_MODEL = "mistral-ocr-latest"
CHAT_MODEL = "mistral-large-latest"
MAX_MARKDOWN_CHARS = 180_000  # keep the prompt within the model context window
MIN_PDF_TEXT_CHARS = 400      # below this, treat the PDF as scanned and fall back to OCR

SYSTEM_PROMPT = (
    "Você extrai dados estruturados de projetos de pesquisa a partir do texto "
    "de um PDF. Responda SOMENTE com um objeto JSON válido, em português, no "
    "formato pedido. Regras gerais: use exatamente as chaves do modelo; se uma "
    "informação não estiver no texto, use null (ou lista vazia) — NUNCA invente "
    "dados; datas no formato ISO (YYYY-MM-DD ou YYYY-MM); valores numéricos sem "
    "símbolo de moeda (ex.: 25000.00).\n"
    "Regras para 'equipe': liste APENAS pessoas reais identificadas por NOME "
    "próprio. O campo 'funcao' é o PAPEL da pessoa (ex.: Coordenador, "
    "Pesquisador, Bolsista, Colaborador, Estudante/Orientando) — NUNCA um título "
    "de plano de trabalho, subprojeto, atividade ou tarefa. Se um item não tiver "
    "nome de pessoa, NÃO o inclua em 'equipe'.\n"
    "Regras para 'cronograma': títulos de planos de trabalho de estudantes, "
    "subprojetos, etapas, atividades ou tarefas pertencem ao 'cronograma' (campo "
    "'atividade'), e NÃO a 'equipe'.\n"
    "Regras para 'coordenador': é o responsável/coordenador do projeto; extraia "
    "o nome mesmo que apareça em seções de identificação, assinatura ou "
    "responsável técnico."
)


def _codigo_from_filename(path: str) -> str:
    """'…/PJ_9760.pdf' -> 'PJ 9760' (authoritative project code from the filename)."""
    stem = os.path.splitext(os.path.basename(path))[0]
    return stem.replace("_", " ").strip()


def _missing_fields(p: Projeto) -> List[str]:
    """List the important fields that came back empty (for `_meta.campos_ausentes`)."""
    missing: List[str] = []
    if not p.titulo:
        missing.append("titulo")
    if not p.descricao:
        missing.append("descricao")
    if not p.area_conhecimento:
        missing.append("area_conhecimento")
    if not p.coordenador.nome:
        missing.append("coordenador.nome")
    if not p.coordenador.email:
        missing.append("coordenador.email")
    if not p.equipe:
        missing.append("equipe")
    if not p.datas.inicio:
        missing.append("datas.inicio")
    if not p.datas.fim:
        missing.append("datas.fim")
    if not p.cronograma:
        missing.append("cronograma")
    if p.financiamento.valor_total is None and not p.financiamento.fontes:
        missing.append("financiamento")
    if not p.objetivos.geral:
        missing.append("objetivos.geral")
    return missing


class ProjectExtractor:
    def __init__(self, api_key: Optional[str] = None,
                 ocr_model: str = OCR_MODEL, chat_model: str = CHAT_MODEL):
        api_key = api_key or os.getenv("MISTRAL_KEY") or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("Set MISTRAL_KEY (or MISTRAL_API_KEY) in the environment/.env")
        self.client = Mistral(api_key=api_key)
        self.ocr_model = ocr_model
        self.chat_model = chat_model

    # --- step 1a: cheap path -- read embedded text locally (no API call) ---
    def pdf_text(self, pdf_path: str) -> Tuple[str, int]:
        """Extract embedded text with pypdf. Returns ("", 0) for scanned PDFs or
        if pypdf is unavailable, so the caller can fall back to OCR."""
        try:
            from pypdf import PdfReader
        except Exception:
            return "", 0
        try:
            reader = PdfReader(pdf_path)
            text = "\n".join((pg.extract_text() or "") for pg in reader.pages)
            return text, len(reader.pages)
        except Exception:
            return "", 0

    # --- step 1b: OCR the PDF to markdown (for scanned PDFs) ---
    def ocr_pdf(self, pdf_path: str) -> Tuple[str, int]:
        """Upload the PDF, OCR it, and return (markdown_text, num_pages)."""
        with open(pdf_path, "rb") as f:
            content = f.read()
        uploaded = self.client.files.upload(
            file={"file_name": os.path.basename(pdf_path), "content": content},
            purpose="ocr",
        )
        signed = self.client.files.get_signed_url(file_id=uploaded.id)
        resp = self.client.ocr.process(
            model=self.ocr_model,
            document={"type": "document_url", "document_url": signed.url},
        )
        pages = resp.pages or []
        markdown = "\n\n".join((pg.markdown or "") for pg in pages)
        return markdown, len(pages)

    # --- prompt shared by the sync and batch paths ---
    def build_messages(self, codigo: str, text: str) -> list:
        """Build the chat messages for one project's structured extraction."""
        user_prompt = (
            f"Código do projeto (use exatamente este valor em 'codigo'): {codigo}\n\n"
            f"Formato JSON esperado (modelo das chaves):\n"
            f"{json.dumps(JSON_TEMPLATE, ensure_ascii=False, indent=2)}\n\n"
            f"Texto do PDF do projeto:\n\"\"\"\n{text[:MAX_MARKDOWN_CHARS]}\n\"\"\""
        )
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

    # --- text source: local first, OCR fallback ---
    def text_for(self, pdf_path: str) -> Tuple[str, int, str]:
        """Return (text, num_pages, source) using embedded text when possible."""
        text, num_pages = self.pdf_text(pdf_path)
        if len(text.strip()) >= MIN_PDF_TEXT_CHARS:
            return text, num_pages, "pdf-text"
        text, num_pages = self.ocr_pdf(pdf_path)
        return text, num_pages, "ocr"

    # --- step 2: structured extraction via chat (JSON mode) ---
    def extract_fields(self, codigo: str, text: str) -> dict:
        resp = self.client.chat.complete(
            model=self.chat_model,
            messages=self.build_messages(codigo, text),
            response_format={"type": "json_object"},
            temperature=0,
        )
        return json.loads(resp.choices[0].message.content)

    # --- post-process a raw extraction dict into a validated Projeto ---
    def finalize(self, codigo: str, raw: dict, arquivo: str,
                 num_pages: int, source: str) -> Projeto:
        raw["codigo"] = codigo  # filename is authoritative
        # Defensive: 'equipe' must be real people. Drop entries without a name
        # (usually mis-classified work-plan/task titles) -> they belong to cronograma.
        equipe = raw.get("equipe")
        if isinstance(equipe, list):
            raw["equipe"] = [
                m for m in equipe
                if isinstance(m, dict) and (m.get("nome") or "").strip()
            ]
        raw["_meta"] = {
            "arquivo": arquivo,
            "paginas": num_pages,
            "extraido_em": datetime.now(timezone.utc).isoformat(),
            "modelo": self.chat_model,
            "fonte_texto": source,
            "campos_ausentes": [],
        }
        projeto = Projeto.model_validate(raw)
        projeto.meta.campos_ausentes = _missing_fields(projeto)
        return projeto

    # --- full synchronous pipeline for one PDF ---
    def extract_project(self, pdf_path: str) -> Projeto:
        codigo = _codigo_from_filename(pdf_path)
        text, num_pages, source = self.text_for(pdf_path)
        raw = self.extract_fields(codigo, text)
        return self.finalize(codigo, raw, os.path.basename(pdf_path), num_pages, source)
