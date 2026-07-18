"""
Pydantic schema for a research project extracted from a SIGPESQ project PDF.

All content fields are Optional: whatever the PDF does not contain is left as
``None`` (or an empty list) -- the extractor never invents data. `Meta` is filled
by our code (not the model) for provenance.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Coordenador(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    campus: Optional[str] = None
    titulacao: Optional[str] = None


class MembroEquipe(BaseModel):
    nome: Optional[str] = None
    funcao: Optional[str] = None
    instituicao: Optional[str] = None
    carga_horaria_semanal: Optional[float] = None


class Datas(BaseModel):
    inicio: Optional[str] = None          # ISO date "YYYY-MM-DD" when available
    fim: Optional[str] = None
    duracao_meses: Optional[int] = None


class CronogramaItem(BaseModel):
    atividade: Optional[str] = None
    inicio: Optional[str] = None          # "YYYY-MM" or "YYYY-MM-DD"
    fim: Optional[str] = None


class FonteFinanciamento(BaseModel):
    fonte: Optional[str] = None
    valor: Optional[float] = None
    tipo: Optional[str] = None


class Financiamento(BaseModel):
    valor_total: Optional[float] = None
    moeda: str = "BRL"
    fontes: List[FonteFinanciamento] = Field(default_factory=list)


class Objetivos(BaseModel):
    geral: Optional[str] = None
    especificos: List[str] = Field(default_factory=list)


class Meta(BaseModel):
    arquivo: str
    paginas: Optional[int] = None
    extraido_em: Optional[str] = None
    modelo: Optional[str] = None
    fonte_texto: Optional[str] = None   # "pdf-text" (local) or "ocr"
    campos_ausentes: List[str] = Field(default_factory=list)


class Projeto(BaseModel):
    codigo: Optional[str] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    palavras_chave: List[str] = Field(default_factory=list)
    area_conhecimento: Optional[str] = None
    linha_pesquisa: Optional[str] = None
    objetivos: Objetivos = Field(default_factory=Objetivos)
    coordenador: Coordenador = Field(default_factory=Coordenador)
    equipe: List[MembroEquipe] = Field(default_factory=list)
    datas: Datas = Field(default_factory=Datas)
    cronograma: List[CronogramaItem] = Field(default_factory=list)
    financiamento: Financiamento = Field(default_factory=Financiamento)
    meta: Meta = Field(..., alias="_meta")

    model_config = {"populate_by_name": True}


# The JSON shape shown to the extraction model (keeps the LLM output aligned with the schema).
JSON_TEMPLATE = {
    "codigo": "PJ 9760",
    "titulo": "string",
    "descricao": "string",
    "palavras_chave": ["string"],
    "area_conhecimento": "string ou null",
    "linha_pesquisa": "string ou null",
    "objetivos": {"geral": "string ou null", "especificos": ["string"]},
    "coordenador": {"nome": "string ou null", "email": "string ou null",
                    "campus": "string ou null", "titulacao": "string ou null"},
    "equipe": [{"nome": "string", "funcao": "string ou null",
                "instituicao": "string ou null", "carga_horaria_semanal": "number ou null"}],
    "datas": {"inicio": "YYYY-MM-DD ou null", "fim": "YYYY-MM-DD ou null",
              "duracao_meses": "number ou null"},
    "cronograma": [{"atividade": "string", "inicio": "YYYY-MM ou null", "fim": "YYYY-MM ou null"}],
    "financiamento": {"valor_total": "number ou null", "moeda": "BRL",
                      "fontes": [{"fonte": "string", "valor": "number ou null", "tipo": "string ou null"}]},
}
