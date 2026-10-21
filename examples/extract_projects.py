"""
Example: extract structured JSON from downloaded project PDFs using the Mistral API.

For each PDF in reports/project_files/*.pdf it runs Mistral OCR + a JSON-mode chat
extraction (see agent_sigpesq.extraction) and writes:
  reports/project_files_json/<code>.json   (one per project, e.g. PJ_9760.json)
  reports/project_files_json/projects.json (combined array)

Setup:
  pip install -e ".[extract]"      # or: pip install "mistralai>=1.9,<2" pydantic python-dotenv
  # .env must contain MISTRAL_KEY=...

Run:
  python examples/extract_projects.py --limit 5      # test with 5 PDFs
  python examples/extract_projects.py                # all downloaded PDFs
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

from dotenv import load_dotenv

from agent_sigpesq.extraction import ProjectExtractor

load_dotenv()


def main() -> int:
    p = argparse.ArgumentParser(description="Extract project JSON from PDFs via Mistral.")
    p.add_argument("--pdf-dir", default="reports/project_files", help="Folder with project PDFs.")
    p.add_argument("--out-dir", default="reports/project_files_json", help="Output folder for JSON.")
    p.add_argument("--limit", type=int, default=None, help="Max PDFs to process (default: all).")
    p.add_argument("--force", action="store_true",
                   help="Re-extract even if the JSON already exists (default: skip existing).")
    args = p.parse_args()

    pdfs = sorted(glob.glob(os.path.join(args.pdf_dir, "*.pdf")))
    if args.limit is not None:
        pdfs = pdfs[: args.limit]
    if not pdfs:
        print(f"No PDFs found in {args.pdf_dir}. Run the PDF ETL first.")
        return 1

    os.makedirs(args.out_dir, exist_ok=True)
    extractor = ProjectExtractor()

    ok = skipped = 0
    for i, pdf in enumerate(pdfs, 1):
        name = os.path.basename(pdf)
        stem = os.path.splitext(name)[0]
        out_path = os.path.join(args.out_dir, f"{stem}.json")
        # resumable: skip PDFs already extracted unless --force
        if not args.force and os.path.exists(out_path):
            skipped += 1
            continue
        print(f"[{i}/{len(pdfs)}] {name} ...", flush=True)
        try:
            projeto = extractor.extract_project(pdf)
        except Exception as e:
            print(f"    FAILED: {e}")
            continue
        data = projeto.model_dump(by_alias=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        ok += 1
        missing = data["_meta"]["campos_ausentes"]
        print(f"    OK -> {stem}.json"
              + (f"  (campos ausentes: {', '.join(missing)})" if missing else ""))

    # rebuild the combined array from ALL per-project JSON files on disk
    combined = []
    for jf in sorted(glob.glob(os.path.join(args.out_dir, "*.json"))):
        if os.path.basename(jf) == "projects.json":
            continue
        with open(jf, encoding="utf-8") as f:
            combined.append(json.load(f))
    with open(os.path.join(args.out_dir, "projects.json"), "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {ok} extracted, {skipped} skipped (already done), "
          f"{len(combined)} in projects.json -> {args.out_dir}/")
    return 0 if (ok > 0 or skipped > 0) else 1


if __name__ == "__main__":
    sys.exit(main())
