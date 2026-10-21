"""
Example: ETL 1 only -- report files (Excel).

Downloads the three report categories via the report buttons on
relatorio/lista.aspx, in a single login:
  - Research Groups   -> reports/research_group/
  - Research Projects -> reports/research_projects/
  - Advisorships      -> reports/advisorships/<year>/

Run it:
    pip install -e .          # or: export PYTHONPATH=src
    python examples/run_reports_etl.py
    python examples/run_reports_etl.py --headful   # watch the browser
"""
from __future__ import annotations

import argparse
import asyncio
import sys

from agent_sigpesq.services.reports_service import SigpesqReportService
from agent_sigpesq.strategies import (
    ResearchGroupsDownloadStrategy,
    ProjectsDownloadStrategy,
    AdvisorshipsDownloadStrategy,
)


async def main(headless: bool, out_dir: str) -> bool:
    service = SigpesqReportService(
        headless=headless,
        download_dir=out_dir,
        strategies=[
            ResearchGroupsDownloadStrategy(),
            ProjectsDownloadStrategy(),
            AdvisorshipsDownloadStrategy(),
        ],
    )
    return await service.run()  # single login


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run the report (Excel) ETL with a single login.")
    p.add_argument("--out", default="reports", help="Output directory (default: reports).")
    p.add_argument("--headful", action="store_true", help="Show the browser window.")
    args = p.parse_args()

    ok = asyncio.run(main(headless=not args.headful, out_dir=args.out))
    print("Reports ETL finished." if ok else "Reports ETL failed.")
    sys.exit(0 if ok else 1)
