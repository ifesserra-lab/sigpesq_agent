"""
Bulk PDF -> JSON extraction via the Mistral Batch API (~50% cheaper, async).

Prepares chat requests from LOCAL pdf text (no API calls during prep), submits
one batch job, polls until it finishes, and writes one JSON per project. Scanned
PDFs (no embedded text) are skipped here -- run extract_projects.py for those.

Setup:
  pip install -e ".[extract]"      # mistralai + pypdf
  # .env must contain MISTRAL_KEY=...

Run:
  python examples/extract_projects_batch.py                 # all not-yet-extracted
  python examples/extract_projects_batch.py --limit 50      # cap request count
  python examples/extract_projects_batch.py --job JOB_ID    # resume: just collect a job
  python examples/extract_projects_batch.py --poll 60       # poll interval (s)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time

from dotenv import load_dotenv

from agent_sigpesq.extraction.batch_extractor import BatchProjectExtractor, TERMINAL_STATES

load_dotenv()


def main() -> int:
    p = argparse.ArgumentParser(description="Bulk project extraction via Mistral Batch API.")
    p.add_argument("--pdf-dir", default="reports/project_files")
    p.add_argument("--out-dir", default="reports/project_files_json")
    p.add_argument("--limit", type=int, default=None, help="Max requests to batch.")
    p.add_argument("--force", action="store_true", help="Include PDFs already extracted.")
    p.add_argument("--poll", type=int, default=30, help="Poll interval in seconds.")
    p.add_argument("--job", default=None, help="Existing batch job id to just collect.")
    args = p.parse_args()

    extractor = BatchProjectExtractor()

    # collect-only mode for an already-submitted job
    if args.job:
        pdfs = sorted(glob.glob(os.path.join(args.pdf_dir, "*.pdf")))
        _, meta, _ = extractor.build_requests(pdfs)  # rebuild custom_id -> meta map
        job = extractor.get_job(args.job)
        written, errors = extractor.collect_results(job, meta, args.out_dir)
        print(f"Collected job {args.job}: {written} written, {errors} errors.")
        return _rebuild_combined(args.out_dir)

    pdfs = sorted(glob.glob(os.path.join(args.pdf_dir, "*.pdf")))
    if not args.force:
        pdfs = [f for f in pdfs
                if not os.path.exists(os.path.join(
                    args.out_dir, os.path.splitext(os.path.basename(f))[0] + ".json"))]
    if args.limit is not None:
        pdfs = pdfs[: args.limit]
    if not pdfs:
        print("Nothing to extract (all done?). Use --force to re-extract.")
        return _rebuild_combined(args.out_dir)

    jsonl, meta, skipped = extractor.build_requests(pdfs)
    print(f"Prepared {len(meta)} batch requests; {len(skipped)} scanned PDF(s) skipped "
          f"(use extract_projects.py for those).")
    if not meta:
        print("No digital PDFs to batch.")
        return 1

    job_id = extractor.submit(jsonl)
    print(f"Submitted batch job: {job_id}", flush=True)

    while True:
        job = extractor.get_job(job_id)
        status = getattr(job, "status", "?")
        done = getattr(job, "completed_requests", None)
        total = getattr(job, "total_requests", None)
        print(f"  status={status} completed={done}/{total}", flush=True)
        if status in TERMINAL_STATES:
            break
        time.sleep(args.poll)

    written, errors = extractor.collect_results(job, meta, args.out_dir)
    print(f"Job {job_id} {getattr(job, 'status', '?')}: {written} written, {errors} errors.")
    return _rebuild_combined(args.out_dir)


def _rebuild_combined(out_dir: str) -> int:
    combined = []
    for jf in sorted(glob.glob(os.path.join(out_dir, "*.json"))):
        if os.path.basename(jf) == "projects.json":
            continue
        with open(jf, encoding="utf-8") as f:
            combined.append(json.load(f))
    if combined:
        with open(os.path.join(out_dir, "projects.json"), "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"projects.json now has {len(combined)} projects.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
