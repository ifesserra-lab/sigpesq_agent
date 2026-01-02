import asyncio

async def main():
    print("Starting Sigpesq Report Download Job...")
    from agent_sigpesq.services.reports_service import SigpesqReportService
    
    # Run in headless mode and save reports to 'reports' folder
    service = SigpesqReportService(headless=True, download_dir="reports")
    success = await service.run()
    
    if success:
        print("Report download job completed successfully!")
    else:
        print("Report download job failed.")

if __name__ == "__main__":
    asyncio.run(main())
