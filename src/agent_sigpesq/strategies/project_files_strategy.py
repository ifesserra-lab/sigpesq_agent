"""
Strategy for downloading the per-project PDF file ("Projeto") of every research
project listed under Diretoria -> Projetos -> do Campus.

Path (discovered on the SIGPESQ portal, all within a SINGLE logged-in session):
  /web/projeto/listaUnidade.aspx
    -> grid #ContentPlaceHolder_gvwLista (10 projects per page, paginated)
       -> per row: click "Resumo do Projeto" button
          (#ContentPlaceHolder_gvwLista_btnResumoProjeto_<i>)
          opens the modal #ContentPlaceHolder_ModalConsultaProjeto (in-page, no navigation)
          -> the modal's "Arquivos" table (rptArquivo) has a download link labeled "Projeto"
             (#ContentPlaceHolder_ModalConsultaProjeto_..._rptArquivo_Download_0)
             -> clicking it (__doPostBack) streams the project PDF
       -> "Fechar" (#ContentPlaceHolder_ModalConsultaProjeto_btnModal_Fechar) closes the modal
    -> pager: __doPostBack('ctl00$ContentPlaceHolder$gvwLista', 'Page$<N>')

This strategy re-navigates to the list page itself; it relies only on the page
already being authenticated. It never logs in again (the portal rate-limits logins).
"""
from __future__ import annotations

import os
import re
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from .report_download_strategy import BasePlaywrightStrategy

BASE = "https://sigpesq.ifes.edu.br/web"
LIST_URL = f"{BASE}/projeto/listaUnidade.aspx"

GRID = "#ContentPlaceHolder_gvwLista"
RESUMO_BTN = "#ContentPlaceHolder_gvwLista_btnResumoProjeto_{i}"
MODAL = "#ContentPlaceHolder_ModalConsultaProjeto"
MODAL_CLOSE = "#ContentPlaceHolder_ModalConsultaProjeto_btnModal_Fechar"
# download links inside the modal's "Arquivos" repeater
MODAL_FILE_LINKS = "[id*='ModalConsultaProjeto'][id*='rptArquivo_Download']"


def _safe_name(text: str) -> str:
    """Turn a project code like 'PJ 9760' into a filesystem-safe stem 'PJ_9760'."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", (text or "").strip()).strip("_") or "projeto"


class ProjectFilesDownloadStrategy(BasePlaywrightStrategy):
    """
    Downloads the "Projeto" PDF of every campus research project via the
    Resumo modal, iterating all grid pages. Single login (reuses the page).
    """

    def __init__(self, limit: int | None = None, file_label: str = "Projeto",
                 skip_existing: bool = True):
        """
        Args:
            limit: max number of projects to process (None = all). Handy for testing.
            file_label: the link text inside the Arquivos table to download
                        ("Projeto" = the main project PDF).
            skip_existing: if True, projects whose PDF is already on disk are skipped
                           (makes a re-run resumable, e.g. after a mid-run stop).
        """
        self.limit = limit
        self.file_label = file_label
        self.skip_existing = skip_existing

    def get_category_name(self) -> str:
        return "Research Project Files"

    def get_button_id(self) -> str:
        # No single button; per-row Resumo buttons are used instead.
        return "ContentPlaceHolder_gvwLista_btnResumoProjeto_0"

    async def download(self, page: Page, reports_dir: str) -> bool:
        print(f"Processing {self.get_category_name()}...")
        target_subdir = os.path.join(reports_dir, "project_files")
        os.makedirs(target_subdir, exist_ok=True)

        try:
            await page.goto(LIST_URL)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector(GRID, timeout=15000)
        except Exception as e:
            print(f"Could not open project list: {e}")
            return False

        total, ok, done = await self._read_total(page), 0, 0
        # total pages = ceil(total / rows_per_page); the portal shows 10 rows/page
        max_pages = (total + 9) // 10 if total else None
        print(f"Total projects reported by portal: {total or 'unknown'}"
              + (f" ({max_pages} pages)" if max_pages else ""))

        page_num = 1
        while True:
            # rows present on the current grid page
            row_count = await page.locator(f"{GRID} a[id*='btnResumoProjeto']").count()
            if row_count == 0:
                print(f"No project rows on page {page_num}; stopping.")
                break

            print(f"--- Grid page {page_num}: {row_count} projects ---")
            for i in range(row_count):
                if self.limit is not None and done >= self.limit:
                    print(f"Reached limit={self.limit}; stopping.")
                    return ok > 0
                done += 1
                code = await self._row_code(page, i, page_num)
                # resumable: skip projects whose PDF is already on disk
                if self.skip_existing and os.path.exists(
                        os.path.join(target_subdir, f"{_safe_name(code)}.pdf")):
                    ok += 1
                    continue
                if await self._download_one(page, i, code, target_subdir):
                    ok += 1
                # after Fechar the grid is re-rendered on the same page; continue

            # advance to next grid page, if any (bounded by the total page count)
            if max_pages is not None and page_num >= max_pages:
                break
            # let the last modal-close postback settle (pager back on page_num) so the
            # next click isn't issued against a still-updating grid
            try:
                await page.wait_for_function(
                    "(n) => { const s = document.querySelector('.gvwPager span');"
                    " return !!s && s.textContent.trim() === String(n); }",
                    arg=page_num, timeout=10000,
                )
            except Exception:
                pass
            if not await self._go_to_page(page, page_num + 1):
                break
            page_num += 1

        print(f"Done. Downloaded {ok} project file(s) into {target_subdir}.")
        return ok > 0

    async def _download_one(self, page: Page, i: int, code: str, target_subdir: str) -> bool:
        """Open the Resumo modal for row i, download the '<file_label>' PDF, close the modal."""
        try:
            await page.click(RESUMO_BTN.format(i=i))
            # the modal opens for any project (even drafts); its "Fechar" button is a
            # reliable "modal is open" signal (the outer modal div has no bounding box).
            await page.wait_for_selector(MODAL_CLOSE, state="visible", timeout=12000)
        except PlaywrightTimeoutError:
            print(f"[{code}] Resumo modal did not open; skipping.")
            await self._close_modal(page)
            return False
        except Exception as e:
            print(f"[{code}] error opening modal: {e}")
            await self._close_modal(page)
            return False

        # drafts have an empty Arquivos table -> no file links -> skip fast (no long wait)
        if await page.locator(MODAL_FILE_LINKS).count() == 0:
            print(f"[{code}] no files in Arquivos (likely a draft); skipping.")
            await self._close_modal(page)
            return False

        # pick the link labeled with file_label (e.g. "Projeto"); fall back to first file
        link = page.locator(MODAL_FILE_LINKS, has_text=self.file_label).first
        if await link.count() == 0:
            link = page.locator(MODAL_FILE_LINKS).first

        try:
            async with page.expect_download(timeout=60000) as dl_info:
                await link.click()
            download = await dl_info.value
            suggested = download.suggested_filename or "projeto.pdf"
            ext = os.path.splitext(suggested)[1] or ".pdf"
            dest = os.path.join(target_subdir, f"{_safe_name(code)}{ext}")
            if os.path.exists(dest):
                os.remove(dest)
            await download.save_as(dest)
            print(f"[{code}] saved -> {dest}")
            return True
        except Exception as e:
            print(f"[{code}] download failed: {e}")
            return False
        finally:
            await self._close_modal(page)

    async def _close_modal(self, page: Page):
        try:
            if await page.locator(MODAL_CLOSE).count() > 0 and await page.is_visible(MODAL_CLOSE):
                await page.click(MODAL_CLOSE)
                await page.wait_for_load_state("networkidle")
        except Exception:
            pass

    async def _go_to_page(self, page: Page, n: int) -> bool:
        """Go to grid page n by clicking its pager link, matched by postback href.

        The pager is windowed: it renders a block of numbers plus a '...' forward
        link and 'Último'. Matching by visible text misses the '...' link at block
        boundaries, so we match by the postback target in the href ('Page$N'),
        which also covers '...'. Navigating sequentially, a link for page N always
        exists (a numeric one inside the block, or '...' at the boundary).
        """
        selector = f".gvwPager a[href*=\"Page${n}'\"]"
        # A modal-close postback from the previous page can still be in flight, so a
        # click can land on a half-rendered/empty grid. Retry the whole click, and
        # only accept it once the pager shows page n AND the grid has project rows.
        landed = (
            "(n) => { const s = document.querySelector('.gvwPager span');"
            " const rows = document.querySelectorAll("
            "\"#ContentPlaceHolder_gvwLista a[id*='btnResumoProjeto']\").length;"
            " return !!s && s.textContent.trim() === String(n) && rows > 0; }"
        )
        for _attempt in range(4):
            link = page.locator(selector).first
            if await link.count() == 0:
                await page.wait_for_timeout(1000)  # pager may still be rendering
                continue
            try:
                await link.click()
                await page.wait_for_function(landed, arg=n, timeout=15000)
                return True
            except Exception:
                await page.wait_for_timeout(1000)  # empty/half-rendered -> retry click
        print(f"Could not load rows for grid page {n} after retries.")
        return False

    async def _row_code(self, page: Page, i: int, page_num: int = 0) -> str:
        """Read the project code (e.g. 'PJ 9760') from row i for use as the filename.

        Falls back to a page-unique placeholder if the code can't be read, so
        unreadable rows on different pages never collide on the same filename.
        """
        try:
            code = await page.evaluate(
                """(i) => {
                    const btns = document.querySelectorAll("#ContentPlaceHolder_gvwLista a[id*='btnResumoProjeto']");
                    const tr = btns[i] && btns[i].closest('tr');
                    if (!tr) return null;
                    for (const td of tr.querySelectorAll('td')) {
                        const m = (td.innerText||'').match(/PJ\\s*\\d+/);
                        if (m) return m[0];
                    }
                    return null;
                }""",
                i,
            )
            return code or f"unknown_p{page_num}r{i}"
        except Exception:
            return f"unknown_p{page_num}r{i}"

    async def _read_total(self, page: Page):
        """Parse 'Mostrando de X até Y de N registro(s)' to get the total count."""
        try:
            txt = await page.locator(".gvwPager").first.inner_text()
            m = re.search(r"de\s+(\d+)\s+registro", txt)
            return int(m.group(1)) if m else None
        except Exception:
            return None
