"""
Bulk PDF -> JSON extraction via the Mistral Batch API (~50% cheaper than
synchronous calls; asynchronous).

Flow:
  1. build a JSONL of chat requests (one line per project), using text read
     locally with pypdf -- no API calls during preparation. Scanned PDFs (no
     embedded text) are skipped here and left to the synchronous extractor.
  2. upload the JSONL (purpose="batch") and create a batch job on
     /v1/chat/completions.
  3. poll the job until it reaches a terminal state.
  4. download the results, validate each into a Projeto, and write the JSON.

The heavy chat calls run inside the batch (discounted). Preparation is offline.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .mistral_extractor import ProjectExtractor, MIN_PDF_TEXT_CHARS, _codigo_from_filename

TERMINAL_STATES = {"SUCCESS", "FAILED", "CANCELLED", "CANCELLATION_REQUESTED",
                   "TIMEOUT_EXCEEDED"}


class BatchProjectExtractor(ProjectExtractor):
    """Prepare, submit, and collect a Mistral batch job for project extraction."""

    def build_requests(self, pdf_paths: List[str]) -> Tuple[str, Dict[str, dict], List[str]]:
        """Return (jsonl_text, meta_by_custom_id, skipped_scanned).

        Only digital PDFs (embedded text) are batched; scanned PDFs are returned
        in `skipped_scanned` so the caller can handle them with the sync path.
        """
        lines: List[str] = []
        meta: Dict[str, dict] = {}
        skipped: List[str] = []
        for pdf in pdf_paths:
            stem = os.path.splitext(os.path.basename(pdf))[0]
            codigo = _codigo_from_filename(pdf)
            text, num_pages = self.pdf_text(pdf)
            if len(text.strip()) < MIN_PDF_TEXT_CHARS:
                skipped.append(pdf)  # scanned -> needs OCR, not batched here
                continue
            body = {
                "messages": self.build_messages(codigo, text),
                "response_format": {"type": "json_object"},
                "temperature": 0,
            }
            lines.append(json.dumps({"custom_id": stem, "body": body}, ensure_ascii=False))
            meta[stem] = {"codigo": codigo, "arquivo": os.path.basename(pdf),
                          "paginas": num_pages, "fonte_texto": "pdf-text"}
        return "\n".join(lines) + ("\n" if lines else ""), meta, skipped

    def submit(self, jsonl_text: str) -> str:
        """Upload the JSONL and create a chat-completions batch job. Returns job id."""
        uploaded = self.client.files.upload(
            file={"file_name": "batch_input.jsonl", "content": jsonl_text.encode("utf-8")},
            purpose="batch",
        )
        job = self.client.batch.jobs.create(
            input_files=[uploaded.id],
            endpoint="/v1/chat/completions",
            model=self.chat_model,
            metadata={"job": "sigpesq-project-extraction"},
        )
        return job.id

    def get_job(self, job_id: str):
        return self.client.batch.jobs.get(job_id=job_id)

    def collect_results(self, job, meta: Dict[str, dict], out_dir: str) -> Tuple[int, int]:
        """Download the job's output file, write one JSON per project.

        Returns (written, errors).
        """
        output_file_id = getattr(job, "output_file", None)
        if not output_file_id:
            return 0, 0
        resp = self.client.files.download(file_id=output_file_id)
        written = errors = 0
        os.makedirs(out_dir, exist_ok=True)
        for raw_line in resp.text.splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                rec = json.loads(raw_line)
                custom_id = rec.get("custom_id")
                info = meta.get(custom_id)
                if not info:
                    continue
                content = rec["response"]["body"]["choices"][0]["message"]["content"]
                data = json.loads(content)
                projeto = self.finalize(
                    info["codigo"], data, info["arquivo"], info["paginas"], info["fonte_texto"]
                )
                with open(os.path.join(out_dir, f"{custom_id}.json"), "w", encoding="utf-8") as f:
                    json.dump(projeto.model_dump(by_alias=True), f, ensure_ascii=False, indent=2)
                written += 1
            except Exception:
                errors += 1
        return written, errors


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
