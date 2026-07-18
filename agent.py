import asyncio
import argparse
import sys
from agent_sigpesq.services.reports_service import SigpesqReportService
from agent_sigpesq.strategies import (
    ResearchGroupsDownloadStrategy,
    ProjectsDownloadStrategy,
    AdvisorshipsDownloadStrategy,
    ProjectFilesDownloadStrategy
)

async def main():
    parser = argparse.ArgumentParser(description="Sigpesq Report Downloader Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Subcommands
    subparsers.add_parser("download-all", help="Download all reports (default)")
    subparsers.add_parser("download-groups", help="Download only Research Groups reports")
    subparsers.add_parser("download-projects", help="Download only Research Projects reports")
    subparsers.add_parser("download-advisorships", help="Download only Advisorships reports")
    pf = subparsers.add_parser(
        "download-project-files",
        help="Download the 'Projeto' PDF of each campus project (Diretoria -> Projetos -> do Campus)"
    )
    pf.add_argument("--limit", type=int, default=None,
                    help="Max number of projects to process (default: all)")
    ev = subparsers.add_parser(
        "download-everything",
        help="Run BOTH ETLs in a SINGLE login: report files (Excel) + per-project PDFs"
    )
    ev.add_argument("--limit", type=int, default=None,
                    help="Max number of projects for the PDF ETL (default: all)")

    args = parser.parse_args()

    strategies = None
    if args.command == "download-groups":
        strategies = [ResearchGroupsDownloadStrategy()]
        print("Configuration: Downloading Research Groups only.")
    elif args.command == "download-projects":
        strategies = [ProjectsDownloadStrategy()]
        print("Configuration: Downloading Research Projects only.")
    elif args.command == "download-advisorships":
        strategies = [AdvisorshipsDownloadStrategy()]
        print("Configuration: Downloading Advisorships only.")
    elif args.command == "download-project-files":
        strategies = [ProjectFilesDownloadStrategy(limit=args.limit)]
        print(f"Configuration: Downloading per-project PDF files (limit={args.limit}).")
    elif args.command == "download-everything":
        # Both ETLs, one login. project-files LAST: it navigates away from the reports page.
        strategies = [
            ResearchGroupsDownloadStrategy(),
            ProjectsDownloadStrategy(),
            AdvisorshipsDownloadStrategy(),
            ProjectFilesDownloadStrategy(limit=args.limit),
        ]
        print(f"Configuration: Running BOTH ETLs (reports + PDFs) in one login (limit={args.limit}).")
    else:
        print("Configuration: Downloading ALL reports.")

    print("Starting Sigpesq Report Download Job...")
    
    # Run in headless mode and save reports to 'reports' folder
    service = SigpesqReportService(headless=True, download_dir="reports", strategies=strategies)
    success = await service.run()
    
    if success:
        print("Report download job completed successfully!")
    else:
        print("Report download job failed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
