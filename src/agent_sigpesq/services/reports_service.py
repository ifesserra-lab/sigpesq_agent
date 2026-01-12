import os
import asyncio
from typing import List, Optional
from playwright.async_api import async_playwright
from dotenv import load_dotenv

from agent_sigpesq.core.browser_factory import BrowserFactory
from agent_sigpesq.strategies.report_download_strategy import ReportDownloadStrategy
from agent_sigpesq.strategies.research_groups_strategy import ResearchGroupsDownloadStrategy
from agent_sigpesq.strategies.projects_strategy import ProjectsDownloadStrategy
from agent_sigpesq.strategies.advisorships_strategy import AdvisorshipsDownloadStrategy

load_dotenv()

class SigpesqReportService:
    """
    Service responsible for orchestrating the download of Sigpesq reports.
    
    Attributes:
        headless (bool): Whether to run the browser in headless mode.
        download_dir (str): Directory where reports will be saved.
    """
    
    def __init__(self, headless: bool = True, download_dir: str = "reports", strategies: Optional[List[ReportDownloadStrategy]] = None):
        """
        Initializes the SigpesqReportService.
        """
        self.username = os.getenv("SIGPESQ_USER")
        self.password = os.getenv("SIGPESQ_PASSWORD")
        self.login_url = "https://sigpesq.ifes.edu.br/Login.aspx"
        self.reports_url = "https://sigpesq.ifes.edu.br/web/relatorio/lista.aspx"
        self.headless = headless
        self.download_dir = download_dir
        
        # Initialize strategies in the order requested by user
        if strategies:
            self.strategies = strategies
        else:
             self.strategies = [
                ResearchGroupsDownloadStrategy(),
                ProjectsDownloadStrategy(),
                AdvisorshipsDownloadStrategy()
            ]

    async def run(self) -> bool:
        """
        Runs the report download process.
        """
        print(f"Initializing Browser (Headless: {self.headless})...")
        
        async with async_playwright() as p:
            context = await BrowserFactory.create_browser_context(p, headless=self.headless)
            page = await context.new_page()
            
            try:
                # Login
                if not await self._login(page):
                    print("Login failed. Aborting.")
                    return False
                
                # Download Reports
                return await self._download_all_reports(page)
                
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                import traceback
                traceback.print_exc()
                return False
            finally:
                await context.close()

    async def _login(self, page) -> bool:
        """
        Performs login on the Sigpesq portal.
        """
        print(f"Navigating to {self.login_url}...")
        await page.goto(self.login_url)
        
        if not self.username or not self.password:
            print("Error: SIGPESQ_USER or SIGPESQ_PASSWORD not set.")
            return False
            
        print("Entering credentials...")
        try:
             # Wait for input to be ready
            await page.wait_for_selector("#txtLogin", state="visible")
            
            await page.fill("#txtLogin", self.username)
            await page.fill("#txtSenha", self.password)
            
            print("Clicking login...")
            await page.click("#btnLogin")
            
            # Wait for navigation or check for success/failure
            # Login successful usually redirects to Default.aspx or similar, or shows user info
            # We wait for URL change or error message
            
            try:
                 # Check for success (URL change)
                await page.wait_for_url("**/web/**", timeout=10000)
                print("Login successful!")
                return True
            except:
                # Check for error message
                if await page.is_visible("#ContentPlaceHolder_lblMsgErro"):
                    msg = await page.text_content("#ContentPlaceHolder_lblMsgErro")
                    print(f"Login failed: {msg}")
                    return False
                
                # If URL didn't change and no error message, assumption: login failed or timed out
                # But sometimes it redirects to a different path
                current_url = page.url
                if "Login.aspx" not in current_url:
                     print("Login successful (URL changed)!")
                     return True
                
                print("Login failed: Unknown error.")
                return False

        except Exception as e:
            print(f"Error during login: {e}")
            return False

    async def _download_all_reports(self, page) -> bool:
        """
        Iterates through configured strategies and downloads reports.
        """
        print(f"Navigating to reports page: {self.reports_url}...")
        await page.goto(self.reports_url)
        
        all_success = True
        
        for strategy in self.strategies:
            print(f"--- Starting Strategy: {strategy.get_category_name()} ---")
            success = await strategy.download(page, self.download_dir)
            if success:
                print(f"Strategy {strategy.get_category_name()} completed successfully.")
            else:
                print(f"Strategy {strategy.get_category_name()} failed.")
                all_success = False
            
        return all_success
