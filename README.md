# Sigpesq Agent

Automated agent for downloading reports from the Sigpesq portal (IFES) using Selenium and Python.

## 📋 Objective

This agent performs automatic login to the Sigpesq portal and downloads research reports in three categories:

- **Research Groups** → `reports/research_groups/`
- **Research Projects** → `reports/projects/`
- **Advisorships** → `reports/advisorships/{year}/` (one file per year, from 2016 to 2025)

## 🛠️ Technologies

- **Python 3.8+** - Programming language
- **Selenium 4.6+** - Browser automation framework
- **Chrome/Chromium** - Web browser for automation
- **python-dotenv** - Environment variable management
- **Pydantic** - Data validation and settings management
- **Design Patterns**: Strategy Pattern, Factory Pattern, Template Method
- **Architecture**: MVC, SOLID principles
- **Documentation**: IEEE 1016 SDD (Software Design Description)

> [!NOTE]
> This library is designed strictly for **downloading files** from the Sigpesq portal. It **does not** interact with or save data to any database. All outputs are saved as files in the local filesystem.

## 🏗️ Architecture

The project follows **SOLID**, **MVC**, and **Strategy Pattern** principles:

- **Strategy Pattern**: Each report category has its own download strategy
- **Factory Pattern**: `BrowserFactory` manages Selenium WebDriver instances
- **IEEE SDD Documentation**: Architecture documented in `docs/sdd.md`

### Folder Structure

```
agent_sigpesq/
├── src/
│   ├── core/
│   │   ├── base_agent.py          # Abstract base class
│   │   └── browser_factory.py     # WebDriver factory
│   ├── services/
│   │   ├── sigpesq_service.py     # Login service
│   │   └── reports_service.py     # Download orchestrator
│   └── strategies/
│       ├── report_download_strategy.py     # Abstract interface
│       ├── research_groups_strategy.py     # Research groups strategy
│       ├── projects_strategy.py            # Projects strategy
│       └── advisorships_strategy.py        # Advisorships strategy (by year)
├── reports/                       # Output directory for reports
├── agent.py                       # Main entry point
└── requirements.txt               # Python dependencies
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Chrome/Chromium installed
- Sigpesq access credentials

### Step by Step

1. **Clone the repository** (if applicable):
   ```bash
   cd /home/paulossjunior/projects/horizon_project/agent_sigpesq
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials**:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your credentials:
   ```env
   SIGPESQ_USER=your_cpf_here
   SIGPESQ_PASSWORD=your_password_here
   ```

## 📖 Usage

### Basic Execution

```bash
python3 agent.py
```

The agent will:
1. Login to Sigpesq
2. Navigate to the reports page
3. Download all reports in the three categories
4. Save files organized by category and year

### Output Structure

After execution, reports will be organized in:

```
reports/
├── research_groups/
│   └── Relatorio_DD_MM_YYYY.xlsx
├── projects/
│   └── Relatorio_DD_MM_YYYY.xlsx
└── advisorships/
    ├── 2016/
    │   └── Relatorio_DD_MM_YYYY.xlsx
    ├── 2017/
    │   └── Relatorio_DD_MM_YYYY.xlsx
    ...
    └── 2025/
        └── Relatorio_DD_MM_YYYY.xlsx
```

### Headless Mode

By default, the agent runs in headless mode (without graphical interface). To run with visible interface (useful for debugging):

Edit `agent.py` and change:
```python
service = SigpesqReportService(headless=False, download_dir="reports")
```

## 🛠️ Development

### Adding a New Report Category

1. Create a new strategy in `src/strategies/`:
   ```python
   from src.strategies.report_download_strategy import ReportDownloadStrategy
   
   class NewCategoryDownloadStrategy(ReportDownloadStrategy):
       def get_category_name(self) -> str:
           return "Category Name"
       
       def get_button_id(self) -> str:
           return "emit_button_id"
       
       def download(self, driver, reports_dir) -> bool:
           # Implement download logic
           pass
   ```

2. Register the strategy in `src/services/reports_service.py`:
   ```python
   self.strategies = [
       ResearchGroupsDownloadStrategy(),
       ProjectsDownloadStrategy(),
       AdvisorshipsDownloadStrategy(),
       NewCategoryDownloadStrategy()  # Add here
   ]
   ```

### Testing

To test only a specific category, create a test script:

```python
import asyncio
from src.services.reports_service import SigpesqReportService
from src.strategies import ResearchGroupsDownloadStrategy

async def test():
    service = SigpesqReportService(headless=True)
    service.strategies = [ResearchGroupsDownloadStrategy()]
    await service.run()

asyncio.run(test())
```

## 📚 Additional Documentation

- **Architecture**: `docs/sdd_sigpesq.md` (IEEE 1016 Software Design Description)
- **Project Constitution**: `constitution.md` (Principles and guidelines)

## ⚠️ Troubleshooting

### Login Error

If login fails intermittently:
- Verify that credentials in `.env` are correct
- Try running in non-headless mode to visualize the problem
- Check if Chrome/Chromium is up to date

### Downloads not appearing

- Check `reports/` folder permissions
- Ensure there is sufficient disk space
- Check execution logs to identify specific errors

### Incompatible ChromeDriver

Selenium 4.6+ automatically manages ChromeDriver. If there are issues:
```bash
pip install --upgrade selenium
```

## 📄 License

This project follows the guidelines defined in `constitution.md`.

## 👥 Contributing

When contributing, follow SOLID principles and keep the IEEE SDD documentation updated.
