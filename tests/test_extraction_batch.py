import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock

import pytest

pytest.importorskip("mistralai")

from agent_sigpesq.extraction.batch_extractor import BatchProjectExtractor  # noqa: E402


def _extractor():
    ex = BatchProjectExtractor(api_key="test-key")
    ex.client = MagicMock()
    return ex


class TestBatchBuild(unittest.TestCase):
    def test_build_requests_batches_digital_skips_scanned(self):
        ex = _extractor()
        # digital: plenty of text; scanned: empty
        def fake_pdf_text(path):
            return ("x" * 1000, 5) if "digital" in path else ("", 0)
        ex.pdf_text = fake_pdf_text

        with tempfile.TemporaryDirectory() as d:
            digital = os.path.join(d, "PJ_100_digital.pdf")
            scanned = os.path.join(d, "PJ_200_scanned.pdf")
            for f in (digital, scanned):
                open(f, "wb").close()
            jsonl, meta, skipped = ex.build_requests([digital, scanned])

        lines = [ln for ln in jsonl.splitlines() if ln.strip()]
        self.assertEqual(len(lines), 1)              # only the digital one
        self.assertEqual(skipped, [scanned])
        rec = json.loads(lines[0])
        self.assertEqual(rec["custom_id"], "PJ_100_digital")
        self.assertEqual(rec["body"]["response_format"], {"type": "json_object"})
        self.assertIn("PJ_100_digital", meta)
        self.assertEqual(meta["PJ_100_digital"]["fonte_texto"], "pdf-text")

    def test_submit_uploads_and_creates_job(self):
        ex = _extractor()
        ex.client.files.upload.return_value = MagicMock(id="file-1")
        ex.client.batch.jobs.create.return_value = MagicMock(id="job-1")
        job_id = ex.submit('{"custom_id":"PJ_1","body":{}}\n')
        self.assertEqual(job_id, "job-1")
        ex.client.files.upload.assert_called_once()
        kwargs = ex.client.batch.jobs.create.call_args.kwargs
        self.assertEqual(kwargs["endpoint"], "/v1/chat/completions")
        self.assertEqual(kwargs["input_files"], ["file-1"])

    def test_collect_results_writes_json(self):
        ex = _extractor()
        chat_body = {"choices": [{"message": {"content": json.dumps({"titulo": "T"})}}]}
        out_line = json.dumps({"custom_id": "PJ_100",
                               "response": {"status_code": 200, "body": chat_body}})
        ex.client.files.download.return_value = MagicMock(text=out_line + "\n")
        job = MagicMock(output_file="out-file-1")
        meta = {"PJ_100": {"codigo": "PJ 100", "arquivo": "PJ_100.pdf",
                           "paginas": 3, "fonte_texto": "pdf-text"}}

        with tempfile.TemporaryDirectory() as out:
            written, errors = ex.collect_results(job, meta, out)
            self.assertEqual((written, errors), (1, 0))
            data = json.load(open(os.path.join(out, "PJ_100.json")))
        self.assertEqual(data["codigo"], "PJ 100")
        self.assertEqual(data["titulo"], "T")
        self.assertEqual(data["_meta"]["fonte_texto"], "pdf-text")
        self.assertEqual(data["_meta"]["paginas"], 3)

    def test_collect_results_no_output_file(self):
        ex = _extractor()
        job = MagicMock(output_file=None)
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(ex.collect_results(job, {}, out), (0, 0))


if __name__ == "__main__":
    unittest.main()
