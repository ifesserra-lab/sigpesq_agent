import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class BrowserFactory:
    """
    Factory for creating Selenium WebDriver instances.
    """
    
    @staticmethod
    def create_chrome_driver(headless: bool = True, download_dir: str = "reports"):
        """
        Creates and configures a Chrome WebDriver.
        """
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        # Ensure download directory is absolute
        abs_download_dir = os.path.abspath(download_dir)
        
        prefs = {
            "download.default_directory": abs_download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            print(f"Error creating Chrome driver: {e}")
            raise
