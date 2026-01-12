import asyncio
import argparse
import sys
from agent_sigpesq.services.reports_service import SigpesqReportService
from agent_sigpesq.strategies import (
    ResearchGroupsDownloadStrategy,
    ProjectsDownloadStrategy,
    AdvisorshipsDownloadStrategy
)

async def main():
    parser = argparse.ArgumentParser(description="Sigpesq Report Downloader Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Subcommands
    subparsers.add_parser("download-all", help="Download all reports (default)")
    subparsers.add_parser("download-groups", help="Download only Research Groups reports")
    subparsers.add_parser("download-projects", help="Download only Research Projects reports")
    subparsers.add_parser("download-advisorships", help="Download only Advisorships reports")

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
