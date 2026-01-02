import os
import time
from typing import List
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from agent_sigpesq.core.base_agent import BaseAgent
from agent_sigpesq.core.browser_factory import BrowserFactory
from agent_sigpesq.strategies import (
    ReportDownloadStrategy,
    ResearchGroupsDownloadStrategy,
    ProjectsDownloadStrategy,
    AdvisorshipsDownloadStrategy
)

load_dotenv()

class SigpesqReportService(BaseAgent[None, bool]):
    """
    Service to handle report downloads on the Sigpesq portal using Selenium.
    Uses Strategy Pattern for different report categories.
    """

    def __init__(self, headless: bool = True, download_dir: str = "reports"):
        self.username = os.getenv("SIGPESQ_USER")
        self.password = os.getenv("SIGPESQ_PASSWORD")
        self.login_url = "https://sigpesq.ifes.edu.br/Login.aspx"
        self.reports_url = "https://sigpesq.ifes.edu.br/web/relatorio/lista.aspx"
        self.headless = headless
        self.download_dir = download_dir
        self.driver = None
        
        # Initialize strategies in the order requested by user
        self.strategies: List[ReportDownloadStrategy] = [
            ResearchGroupsDownloadStrategy(),
            ProjectsDownloadStrategy(),
            AdvisorshipsDownloadStrategy()
        ]

    def _init_driver(self):
        if not self.driver:
            self.driver = BrowserFactory.create_chrome_driver(
                headless=self.headless, 
                download_dir=self.download_dir
            )
            
            # Enable downloads in headless mode for Chromium/Chrome
            self.driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                'behavior': 'allow',
                'downloadPath': os.path.abspath(self.download_dir)
            })

    async def run(self, input_data: None = None) -> bool:
        try:
            # Ensure reports dir exists
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
            
            self._init_driver()
            if not self._login():
                print("Aborting: Login failed.")
                return False

            return self._download_all_reports()
        finally:
            # Final check for files
            if os.path.exists(self.download_dir):
                files = os.listdir(self.download_dir)
                print(f"\nFinal files in {self.download_dir}: {files}")
                print(f"Total reports downloaded: {len(files)}")
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _login(self) -> bool:
        if not self.username or not self.password:
            print("Error: SIGPESQ_USER or SIGPESQ_PASSWORD not set in .env")
            return False

        print(f"Navigating to {self.login_url}...")
        self.driver.get(self.login_url)
        
        wait = WebDriverWait(self.driver, 20)
        
        try:
            # Wait for any input to ensure page is loaded
            wait.until(EC.presence_of_element_located((By.ID, "txtLogin")))
            
            cpf_field = self.driver.find_element(By.ID, "txtLogin")
            pwd_field = self.driver.find_element(By.ID, "txtSenha")
            btn_login = self.driver.find_element(By.ID, "btnLogin")
            
            # Using ActionChains for CPF due to mask
            actions = ActionChains(self.driver)
            actions.move_to_element(cpf_field).click().perform()
            
            cpf_field.send_keys(Keys.CONTROL + "a")
            cpf_field.send_keys(Keys.BACKSPACE)
            
            print("Typing credentials...")
            for digit in self.username:
                cpf_field.send_keys(digit)
                time.sleep(0.05)
            
            pwd_field.clear()
            pwd_field.send_keys(self.password)
            
            btn_login.click()
            
            # Wait for dashboard
            try:
                wait.until(lambda d: "Dashboard" in d.title or "Dashboard" in d.page_source)
                print("Login successful.")
                return True
            except TimeoutException:
                print("Login verification timed out.")
                # self.driver.save_screenshot("login_timeout_debug.png")
                return False
        except Exception as e:
            print(f"Error during login process: {e}")
            # self.driver.save_screenshot("login_exception_debug.png")
            return False

    def _download_all_reports(self) -> bool:
        """
        Download all reports using the Strategy Pattern.
        Each strategy handles its own category.
        """
        abs_reports_dir = os.path.abspath(self.download_dir)
        success_count = 0
        
        for strategy in self.strategies:
            # Navigate to reports page for each category (fresh state)
            print(f"\nNavigating to {self.reports_url}...")
            self.driver.get(self.reports_url)
            time.sleep(2)
            
            # Execute the strategy
            if strategy.download(self.driver, abs_reports_dir):
                success_count += 1
        
        print(f"\n{'='*50}")
        print(f"Download Summary: {success_count}/{len(self.strategies)} reports downloaded successfully")
        print(f"{'='*50}")
        
        return success_count > 0
