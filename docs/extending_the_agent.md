# Extending the Sigpesq Agent

This guide explains how to extend the Sigpesq Agent by adding new report download strategies. The agent is designed using the **Strategy Pattern**, making it easy to add new report types without modifying existing logic.

## Architecture Overview

The core of the extension mechanism is the `BaseSeleniumStrategy` class, which implements the `ReportDownloadStrategy` interface and provides shared utilities for Selenium interactions.

### Base Paths
- **Interface/Base Class**: `src/strategies/report_download_strategy.py`
- **Concrete Strategies**: `src/strategies/*.py`
- **Registration**: `src/services/reports_service.py`

## Step-by-Step Guide

### 1. Identify Target Elements
Before writing code, inspect the Sigpesq page to identify:
1.  **Accordion Header Text**: The text on the accordion section (e.g., "Grupos de Pesquisa").
2.  **Download Button ID**: The ID of the button that triggers the report generation (e.g., `ContentPlaceHolder_btnRel_GruposPesquisa`).

### 2. Create the Strategy Class
Create a new file in `src/strategies/` (e.g., `my_new_strategy.py`). Inherit from `BaseSeleniumStrategy` and implement the abstract methods.

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os
from src.strategies.report_download_strategy import BaseSeleniumStrategy

class MyNewStrategy(BaseSeleniumStrategy):
    def get_category_name(self) -> str:
        """Returns the human-readable name of this report category."""
        return "My New Report"

    def get_button_id(self) -> str:
        """Returns the ID of the download button."""
        return "ContentPlaceHolder_btnRel_MyNewReport"

    def download(self, driver, reports_dir) -> bool:
        """
        Executes the download logic.
        """
        print(f"Processing {self.get_category_name()}...")
        wait = WebDriverWait(driver, 10)
        
        try:
            # 1. Ensure the accordion is open
            # This helper checks if the button is visible; if not, it finds and clicks the accordion header.
            # You must pass the button ID and the text on the accordion header.
            self._ensure_accordion_open(wait, self.get_button_id(), "Accordion Header Text")

            # 2. Click the download button
            print(f"Clicking button {self.get_button_id()}...")
            driver.find_element(By.ID, self.get_button_id()).click()

            # 3. Wait for the file and move it
            # Define where you want the file to go relative to the main reports directory.
            target_dir = os.path.join(reports_dir, "my_new_report_folder")
            
            # This helper waits for a new file in the downloads folder and moves it to target_dir.
            return self._wait_and_move_file(reports_dir, target_dir)

        except Exception as e:
            print(f"Error downloading {self.get_category_name()}: {e}")
            return False
```

### 3. Register the Strategy
Open `src/services/reports_service.py` and add your new strategy to the list in `__init__`.

```python
from src.strategies.my_new_strategy import MyNewStrategy # Import your class

class SigpesqReportService:
    def __init__(self, headless=True, download_dir="reports"):
        # ...
        self.strategies = [
            ResearchGroupsDownloadStrategy(),
            ProjectsDownloadStrategy(),
            AdvisorshipsDownloadStrategy(),
            MyNewStrategy()  # <--- Register it here
        ]
```

## Shared Utilities (`BaseSeleniumStrategy`)

The base class provides two critical helper methods to standard behavior and reduce code duplication.

### `_ensure_accordion_open(wait, button_id, accordion_text)`
*   **Purpose**: Ensures the UI section containing your button is expanded.
*   **Logic**:
    1.  Checks if the element with `button_id` is already visible.
    2.  If not, searches for an accordion header containing `accordion_text`.
    3.  Clicks the header to expand it.

### `_wait_and_move_file(download_dir, target_dir, timeout=60)`
*   **Purpose**: Handles the asynchronous nature of file downloads.
*   **Logic**:
    1.  Waits for a file ending in `.xlsx` to appear in the default `download_dir` (which matches the project root).
    2.  Creates `target_dir` if it doesn't exist.
    3.  Moves and renames the file to `Relatorio_DD_MM_YYYY.xlsx` in the target directory.
    4.  Returns `True` on success, `False` on timeout.

## Best Practices
1.  **Unique Folder Names**: Ensure your `target_dir` is unique to avoid overwriting other reports.
2.  **Error Handling**: Wrap your logic in `try/except` blocks to prevent one failure from crashing the entire agent.
3.  **Logging**: Use `print` (or a logger) to indicate progress steps ("Clicking...", "Waiting...", "Done").
