import os
from playwright.async_api import Page
from .report_download_strategy import BasePlaywrightStrategy

class ProjectsDownloadStrategy(BasePlaywrightStrategy):
    """
    Strategy for downloading reports related to Research Projects.
    """

    def get_category_name(self) -> str:
        """Returns the category name 'Research Projects'."""
        return "Research Projects"
        
    def get_button_id(self) -> str:
        """Returns the button ID for Research Projects."""
        return "ContentPlaceHolder_btnRel_Projetos"
        
    async def download(self, page: Page, reports_dir: str) -> bool:
        """
        Executes the download simulation for Research Projects.
        """
        print(f"Processing {self.get_category_name()}...")
        
        try:
            # 1. Prepare target subdirectory
            reports_subdir = os.path.join(reports_dir, "research_projects")
            
            button_id = self.get_button_id()
            
            # 2. Ensure accordion is open
            await self._ensure_accordion_open(page, button_id, "Projetos de Pesquisa")
            
            # 3. Handle download
            selector = f"#{button_id}"
            return await self._handle_download_and_move(page, selector, reports_dir, reports_subdir)
            
        except Exception as e:
            print(f"Error downloading {self.get_category_name()}: {e}")
            return False
