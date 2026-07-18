"""
Example: ETL 2 only -- per-project PDFs.

Downloads the "Projeto" PDF of every campus research project
(Diretoria > Projetos > do Campus) in a single login:
  reports/project_files/<project-code>.pdf   e.g. PJ_9760.pdf

Draft projects ("Salvo") have no uploaded file and are skipped.

Run it:
    pip install -e .          # or: export PYTHONPATH=src
    python examples/run_pdf_etl.py               # all ~370 projects
    python examples/run_pdf_etl.py --limit 5     # quick test
    python examples/run_pdf_etl.py --headful     # watch the browser
"""
from __future__ import annotations

import argparse
import asyncio
import sys

from agent_sigpesq.services.reports_service import SigpesqReportService
from agent_sigpesq.strategies import ProjectFilesDownloadStrategy


async def main(limit: int | None, headless: bool, out_dir: str) -> bool:
    service = SigpesqReportService(
        headless=headless,
        download_dir=out_dir,
        strategies=[ProjectFilesDownloadStrategy(limit=limit)],
    )
    return await service.run()  # single login


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run the per-project PDF ETL with a single login.")
    p.add_argument("--limit", type=int, default=None, help="Max projects (default: all).")
    p.add_argument("--out", default="reports", help="Output directory (default: reports).")
    p.add_argument("--headful", action="store_true", help="Show the browser window.")
    args = p.parse_args()

    ok = asyncio.run(main(limit=args.limit, headless=not args.headful, out_dir=args.out))
    print("PDF ETL finished." if ok else "PDF ETL failed.")
    sys.exit(0 if ok else 1)
