"""
Example: run BOTH SIGPESQ ETLs with a SINGLE login.

  ETL 1 (report files / Excel): Research Groups, Research Projects, Advisorships
                                -> downloaded via the report buttons on relatorio/lista.aspx
  ETL 2 (per-project PDFs):     the "Projeto" PDF of every campus project
                                -> Diretoria > Projetos > do Campus

WHY one login: the SIGPESQ portal rate-limits logins ("Muitas tentativas.
Aguarde alguns segundos."). Running the two ETLs as two separate processes logs
in twice and can trip that limit. `SigpesqReportService.run()` logs in ONCE and
then reuses the same authenticated page for every strategy, so we pass all the
strategies to a single service instance.

Order matters: ProjectFilesDownloadStrategy must come LAST because it navigates
away from the reports page to projeto/listaUnidade.aspx.

Run it:
    pip install -e .          # or: export PYTHONPATH=src
    # put SIGPESQ_USER / SIGPESQ_PASSWORD in .env
    python examples/run_all_etls.py
    python examples/run_all_etls.py --limit 5      # cap the PDF ETL for a quick test
    python examples/run_all_etls.py --headful      # watch the browser
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
    ProjectFilesDownloadStrategy,
)


async def main(limit: int | None, headless: bool, out_dir: str) -> bool:
    service = SigpesqReportService(
        headless=headless,
        download_dir=out_dir,
        strategies=[
            # --- ETL 1: report files (Excel) ---
            ResearchGroupsDownloadStrategy(),
            ProjectsDownloadStrategy(),
            AdvisorshipsDownloadStrategy(),
            # --- ETL 2: per-project PDFs (keep LAST: it navigates away) ---
            ProjectFilesDownloadStrategy(limit=limit),
        ],
    )
    # ONE login here drives BOTH ETLs.
    return await service.run()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run both SIGPESQ ETLs with a single login.")
    p.add_argument("--limit", type=int, default=None,
                   help="Max projects for the PDF ETL (default: all 370).")
    p.add_argument("--out", default="reports", help="Output directory (default: reports).")
    p.add_argument("--headful", action="store_true", help="Show the browser window.")
    args = p.parse_args()

    ok = asyncio.run(main(limit=args.limit, headless=not args.headful, out_dir=args.out))
    print("All ETLs finished." if ok else "One or more ETLs failed.")
    sys.exit(0 if ok else 1)
