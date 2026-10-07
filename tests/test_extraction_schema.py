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
        self.assertEqual(p.bolsas, [])

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
            "equipe": [{
                "nome": "Ana",
                "funcao": "Bolsista",
                "carga_horaria_semanal": 12,
                "fonte_bolsa": "CNPq",
            }],
            "cronograma": [{"atividade": "Coleta", "inicio": "2026-03", "fim": "2026-05"}],
            "financiamento": {"valor_total": 1000.0, "fontes": [{"fonte": "CNPq", "valor": 1000.0}]},
            "bolsas": [{
                "tipo": "PIBIC",
                "fonte": "Chamada CNPq 01/2026",
                "orgao_pagador": "CNPq",
                "e_parceria": False,
                "parceiro": None,
                "beneficiario": "Ana",
                "valor": 700.0,
            }],
        })
        self.assertEqual(p.equipe[0].nome, "Ana")
        self.assertEqual(p.equipe[0].carga_horaria_semanal, 12)
        self.assertEqual(p.equipe[0].fonte_bolsa, "CNPq")
        self.assertEqual(p.cronograma[0].atividade, "Coleta")
        self.assertEqual(p.financiamento.fontes[0].fonte, "CNPq")
        self.assertEqual(len(p.bolsas), 1)
        self.assertEqual(p.bolsas[0].tipo, "PIBIC")
        self.assertEqual(p.bolsas[0].orgao_pagador, "CNPq")
        self.assertFalse(p.bolsas[0].e_parceria)
        self.assertEqual(p.bolsas[0].beneficiario, "Ana")
        self.assertEqual(p.bolsas[0].valor, 700.0)

    def test_json_template_has_expected_keys(self):
        for key in ("codigo", "titulo", "descricao", "coordenador", "equipe",
                    "datas", "cronograma", "financiamento", "objetivos", "bolsas"):
            self.assertIn(key, JSON_TEMPLATE)
        self.assertIn("fonte_bolsa", JSON_TEMPLATE["equipe"][0])
        self.assertIn("orgao_pagador", JSON_TEMPLATE["bolsas"][0])
        self.assertIn("e_parceria", JSON_TEMPLATE["bolsas"][0])


if __name__ == "__main__":
    unittest.main()
