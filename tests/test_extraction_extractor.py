import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("mistralai")  # extractor needs the optional mistralai dependency

from agent_sigpesq.extraction.mistral_extractor import (  # noqa: E402
    ProjectExtractor,
    _codigo_from_filename,
    _missing_fields,
)
from agent_sigpesq.extraction.schema import Projeto  # noqa: E402


def _make_extractor_with_mock(chat_payload: dict, pages_markdown):
    """Build a ProjectExtractor whose Mistral client is fully mocked."""
    ex = ProjectExtractor(api_key="test-key")
    ex.client = MagicMock()
    ex.client.files.upload.return_value = MagicMock(id="file-123")
    ex.client.files.get_signed_url.return_value = MagicMock(url="https://signed.example/doc")
    ex.client.ocr.process.return_value = MagicMock(
        pages=[MagicMock(markdown=md) for md in pages_markdown]
    )
    ex.client.chat.complete.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=json.dumps(chat_payload)))]
    )
    return ex


class TestHelpers(unittest.TestCase):
    def test_codigo_from_filename(self):
        self.assertEqual(_codigo_from_filename("/x/reports/PJ_9760.pdf"), "PJ 9760")

    def test_missing_fields_flags_empty(self):
        p = Projeto.model_validate({"titulo": "T", "_meta": {"arquivo": "PJ_1.pdf"}})
        missing = _missing_fields(p)
        self.assertNotIn("titulo", missing)
        self.assertIn("descricao", missing)
        self.assertIn("coordenador.nome", missing)
        self.assertIn("equipe", missing)
        self.assertIn("cronograma", missing)


class TestProjectExtractor(unittest.TestCase):
    def test_missing_api_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                ProjectExtractor(api_key=None)

    def test_ocr_pdf_concatenates_pages(self):
        ex = _make_extractor_with_mock({}, ["# Page1", "Page2 text"])
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tf:
            tf.write(b"%PDF-1.7 dummy")
            tf.flush()
            md, n = ex.ocr_pdf(tf.name)
        self.assertEqual(n, 2)
        self.assertIn("Page1", md)
        self.assertIn("Page2 text", md)
        ex.client.files.upload.assert_called_once()
        ex.client.ocr.process.assert_called_once()

    def test_extract_fields_uses_json_mode(self):
        ex = _make_extractor_with_mock({"titulo": "X"}, ["md"])
        out = ex.extract_fields("PJ 1", "some markdown")
        self.assertEqual(out["titulo"], "X")
        kwargs = ex.client.chat.complete.call_args.kwargs
        self.assertEqual(kwargs["response_format"], {"type": "json_object"})
        self.assertEqual(kwargs["model"], ex.chat_model)

    def test_extract_project_builds_validated_projeto(self):
        payload = {
            "titulo": "Projeto X",
            "descricao": "Uma descrição.",
            "coordenador": {"nome": "Fulano de Tal", "campus": "Serra"},
            "equipe": [{"nome": "Ana", "funcao": "Bolsista"}],
            "codigo": "WRONG",  # must be overridden by the filename
        }
        ex = _make_extractor_with_mock(payload, ["# Projeto", "conteudo"])
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "PJ_9999.pdf")
            with open(pdf, "wb") as f:
                f.write(b"%PDF-1.7 dummy")
            projeto = ex.extract_project(pdf)

        self.assertEqual(projeto.codigo, "PJ 9999")          # filename authoritative
        self.assertEqual(projeto.titulo, "Projeto X")
        self.assertEqual(projeto.coordenador.nome, "Fulano de Tal")
        self.assertEqual(projeto.equipe[0].nome, "Ana")
        # _meta filled by our code
        self.assertEqual(projeto.meta.arquivo, "PJ_9999.pdf")
        self.assertEqual(projeto.meta.paginas, 2)
        self.assertEqual(projeto.meta.modelo, ex.chat_model)
        # campos_ausentes computed: datas/cronograma/financiamento missing, titulo present
        self.assertIn("datas.inicio", projeto.meta.campos_ausentes)
        self.assertIn("cronograma", projeto.meta.campos_ausentes)
        self.assertNotIn("titulo", projeto.meta.campos_ausentes)

    def test_extract_project_uses_pdf_text_and_skips_ocr(self):
        # digital PDF: embedded text is used, OCR call is skipped (cheaper)
        ex = _make_extractor_with_mock({"titulo": "T"}, ["should-not-be-used"])
        ex.pdf_text = lambda p: ("x" * 1000, 5)  # plenty of embedded text
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "PJ_5.pdf")
            with open(pdf, "wb") as f:
                f.write(b"%PDF-1.7 dummy")
            projeto = ex.extract_project(pdf)

        self.assertEqual(projeto.meta.fonte_texto, "pdf-text")
        self.assertEqual(projeto.meta.paginas, 5)
        ex.client.ocr.process.assert_not_called()  # no OCR call for digital PDFs

    def test_extract_project_falls_back_to_ocr_when_no_text(self):
        ex = _make_extractor_with_mock({"titulo": "T"}, ["ocr text"])
        ex.pdf_text = lambda p: ("", 0)  # scanned PDF, no embedded text
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "PJ_6.pdf")
            with open(pdf, "wb") as f:
                f.write(b"%PDF-1.7 dummy")
            projeto = ex.extract_project(pdf)

        self.assertEqual(projeto.meta.fonte_texto, "ocr")
        ex.client.ocr.process.assert_called_once()

    def test_extract_project_drops_nameless_equipe(self):
        # nameless entries are mis-classified work-plan/task titles -> must be dropped
        payload = {
            "titulo": "T",
            "equipe": [
                {"nome": "Maria Silva", "funcao": "Coordenadora"},
                {"nome": None, "funcao": "Plano de trabalho do estudante 1 (PIBIC)"},
                {"nome": "  ", "funcao": "Subprojeto X"},
            ],
        }
        ex = _make_extractor_with_mock(payload, ["md"])
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "PJ_9674.pdf")
            with open(pdf, "wb") as f:
                f.write(b"%PDF-1.7 dummy")
            projeto = ex.extract_project(pdf)

        self.assertEqual(len(projeto.equipe), 1)
        self.assertEqual(projeto.equipe[0].nome, "Maria Silva")


if __name__ == "__main__":
    unittest.main()
