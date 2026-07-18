import unittest

from agent_sigpesq.extraction.schema import Projeto, JSON_TEMPLATE


class TestProjetoSchema(unittest.TestCase):
    def test_minimal_payload_validates_with_defaults(self):
        p = Projeto.model_validate({"codigo": "PJ 1", "_meta": {"arquivo": "PJ_1.pdf"}})
        # content defaults
        self.assertEqual(p.codigo, "PJ 1")
        self.assertIsNone(p.titulo)
        self.assertEqual(p.palavras_chave, [])
        self.assertEqual(p.equipe, [])
        self.assertIsNone(p.coordenador.nome)
        self.assertEqual(p.financiamento.moeda, "BRL")
        self.assertEqual(p.objetivos.especificos, [])

    def test_meta_alias_roundtrip(self):
        p = Projeto.model_validate({"_meta": {"arquivo": "PJ_1.pdf", "paginas": 3}})
        dumped = p.model_dump(by_alias=True)
        self.assertIn("_meta", dumped)
        self.assertNotIn("meta", dumped)
        self.assertEqual(dumped["_meta"]["arquivo"], "PJ_1.pdf")
        self.assertEqual(dumped["_meta"]["paginas"], 3)

    def test_nested_models_parse(self):
        p = Projeto.model_validate({
            "_meta": {"arquivo": "PJ_9.pdf"},
            "equipe": [{"nome": "Ana", "funcao": "Bolsista", "carga_horaria_semanal": 12}],
            "cronograma": [{"atividade": "Coleta", "inicio": "2026-03", "fim": "2026-05"}],
            "financiamento": {"valor_total": 1000.0, "fontes": [{"fonte": "CNPq", "valor": 1000.0}]},
        })
        self.assertEqual(p.equipe[0].nome, "Ana")
        self.assertEqual(p.equipe[0].carga_horaria_semanal, 12)
        self.assertEqual(p.cronograma[0].atividade, "Coleta")
        self.assertEqual(p.financiamento.fontes[0].fonte, "CNPq")

    def test_json_template_has_expected_keys(self):
        for key in ("codigo", "titulo", "descricao", "coordenador", "equipe",
                    "datas", "cronograma", "financiamento", "objetivos"):
            self.assertIn(key, JSON_TEMPLATE)


if __name__ == "__main__":
    unittest.main()
