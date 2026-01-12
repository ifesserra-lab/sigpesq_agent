# 1. Use Playwright for Browser Automation

Date: 2026-01-12

## Status

Accepted

## Context

The `sigpesq_agent` project requires automated interaction with the Sigpesq web portal to authenticate users and download Excel reports. Initially, the project used **Selenium WebDriver** for this purpose. However, we encountered several challenges:

1.  **Reliability Issues**: Frequent timeouts and "element not interactable" errors, particularly with the specific implementation of ASP.NET WebForms postbacks and overlays on the Sigpesq site.
2.  **Performance**: Selenium execution was relatively slow.
3.  **Driver Management**: Managing the correct `chromedriver` version matching the installed browser was improved by `webdriver-manager`, but still introduced friction.
4.  **DevTools Protocol (CDP)**: We needed better control over network events and downloads, which is more native and robust in Playwright (via CDP) than in Selenium.

## Decision

We will replace **Selenium** with **Playwright** (specifically `playwright-python` async API) as the browser automation tool for the `sigpesq_agent`.

## Consequences

### Positive

*   **Improved Reliability**: Playwright's auto-waiting mechanisms and better handling of dynamic content (like the ASP.NET update panels) have significantly reduced flakiness.
*   **Performance**: Playwright is generally faster and supports headless operation more seamlessly.
*   **Simplified Dependency Management**: `playwright install` manages the browser binaries directly, decoupling them from the user's system Chrome installation to some extent.
*   **Better API**: The `async/await` API is modern and fits well with the project's asynchronous goals.
*   **Debugging**: Better debugging tools (Trace Viewer, screenshots on failure) are available.

### Negative

*   **Migration Effort**: Required refactoring `BrowserFactory`, `SigpesqReportService`, and all concrete `ReportDownloadStrategy` implementations.
*   **Dependencies**: Adds `playwright` generic dependencies (browsers) which might be larger to install initially (requires `playwright install`).

### Compliance

*   The implementation adheres to the project's architecture, injecting the `Page` object into strategies.
*   Unit tests were updated to mock Playwright objects (`AsyncMock`), maintaining test coverage.
