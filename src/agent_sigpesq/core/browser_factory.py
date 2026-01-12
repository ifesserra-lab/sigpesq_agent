from playwright.async_api import BrowserContext, Playwright

class BrowserFactory:
    """
    Factory for creating Playwright browser contexts.
    """
    
    @staticmethod
    async def create_browser_context(playwright: Playwright, headless: bool = True) -> BrowserContext:
        """
        Creates and configures a Chrome browser context.
        
        Args:
            playwright: The Playwright instance.
            headless (bool): Whether to run in headless mode.
            
        Returns:
            BrowserContext: Configured browser context.
        """
        browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080"
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        return context
