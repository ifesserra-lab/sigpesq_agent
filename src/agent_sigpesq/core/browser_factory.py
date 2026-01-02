"""
Module for browser creation and configuration.

This module provides a factory class for creating Selenium WebDriver instances
with standardized configurations for this project, including headless mode
and download settings.
"""

import os
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class BrowserFactory:
    """
    Factory for creating Selenium WebDriver instances.
    
    This class encapsulates the configuration and instantiation logic for
    web drivers to ensure consistency across the application.
    """
    
    @staticmethod
    def create_chrome_driver(headless: bool = True, download_dir: str = "reports") -> webdriver.Chrome:
        """
        Creates and configures a Chrome WebDriver.

        Args:
            headless (bool): Whether to run the browser in headless mode. Defaults to True.
            download_dir (str): Relative or absolute path to the directory where downloads should be saved. 
                                Defaults to "reports".

        Returns:
            webdriver.Chrome: A configured Chrome WebDriver instance.

        Raises:
            Exception: If the driver cannot be installed or initialized.
        """
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-software-rasterizer")
        
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
            # Rely on Selenium Manager (Selenium 4.10+) to handle driver installation
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"Error creating Chrome driver: {e}")
            raise
