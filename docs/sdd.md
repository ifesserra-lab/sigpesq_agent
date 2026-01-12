# Software Design Description (SDD) - Sigpesq Login Agent
**Standard: IEEE 1016-2009**

## 1. Introduction
### 1.1 Purpose
This document describes the design of an agentic application for automated data collection from the Sigpesq portal, focusing on the authentication module.

### 1.2 Scope
The scope includes the browser-based interaction, credential management, and navigation to the authenticated dashboard using the `browser-use` library.

## 2. Architectural Design
The system follows a modular architecture based on MVC and SOLID principles.

### 2.1 Component Diagram (Simplified)
- **Agent Job**: Entry point that coordinates the execution.
- **Service Layer**: Manages the browser session and interaction logic using `browser-use`.
- **Core Abstraction**: Abstract classes for agents to ensure consistency and reuse.

## 3. Detailed Design
### 3.1 Core Module
- **BaseAgent (Abstract)**: Defines the interface for all agents in the project. Use Generics for flexible input/output.

### 3.2 Service Module
- **SigpesqLoginService**: Implements the specific logic for authentication.
- **SigpesqReportService**: Handles navigation to `https://sigpesq.ifes.edu.br/web/relatorio/lista.aspx` and orchestrates strategies.
- **Strategies**:
    - **ReportDownloadStrategy (Interface)**: Defines the contract for download strategies.
    - **BaseSeleniumStrategy (Abstract)**: Implements common Selenium logic (accordion handling, file moving).
    - **Concrete Strategies**: `ResearchGroupsDownloadStrategy`, `ProjectsDownloadStrategy`, `AdvisorshipsDownloadStrategy`.

### 3.3 Data Design
- Credentials are read from environment variables (.env).
- Reports are saved to a local `reports/` folder.

### 3.4 CLI Design
The `agent.py` entry point will be refactored to use `argparse` to support subcommands:
- `download-all`: Executes all configured strategies (default).
- `download-groups`: Executes only `ResearchGroupsDownloadStrategy`.
- `download-projects`: Executes only `ProjectsDownloadStrategy`.
- `download-advisorships`: Executes only `AdvisorshipsDownloadStrategy`.

## 4. User Interface Design
Automated interaction via Selenium. The report service will navigate to the reports list and click expansion/download buttons sequentially.

## 5. Design Patterns applied
- **MVC**: Controller (Job), Service (ReportService).
- **Strategy/Template Method**: Used in BaseAgent.
- **SOLID**: Single Responsibility (ReportService focuses on document generation).
- **Factory**: BrowserFactory for WebDriver configuration.
