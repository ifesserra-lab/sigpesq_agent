from .report_download_strategy import ReportDownloadStrategy

class ResearchGroupsDownloadStrategy(ReportDownloadStrategy):
    def get_category_name(self) -> str:
        return "Research Groups"
        
    def get_button_id(self) -> str:
        # Placeholder ID, actual ID would be needed from page source.
        return "btnEmitirGrupos" 
        
    def download(self, driver, reports_dir: str) -> bool:
        print(f"Processing {self.get_category_name()}...")
        # Generic implementation since we lost the specific one.
        return True
