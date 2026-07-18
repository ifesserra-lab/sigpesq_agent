import os
import tempfile
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from agent_sigpesq.strategies.project_files_strategy import (
    ProjectFilesDownloadStrategy,
    _safe_name,
)


class FakeDownloadInfo:
    """Mimics Playwright's `page.expect_download()` async context manager."""

    def __init__(self, download):
        self._download = download

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    @property
    def value(self):
        async def _resolve():
            return self._download
        return _resolve()


def _locator(count=1, inner_text=""):
    """A Locator mock where `.first` returns itself and async calls resolve."""
    m = MagicMock()
    m.first = m
    m.count = AsyncMock(return_value=count)
    m.click = AsyncMock()
    m.filter = MagicMock(return_value=m)
    m.inner_text = AsyncMock(return_value=inner_text)
    return m


class TestSafeName(unittest.TestCase):
    def test_code_to_stem(self):
        self.assertEqual(_safe_name("PJ 9760"), "PJ_9760")

    def test_strips_unsafe_chars(self):
        self.assertEqual(_safe_name("PJ/97*60?"), "PJ_97_60")

    def test_empty_falls_back(self):
        self.assertEqual(_safe_name("   "), "projeto")


class TestProjectFilesDownloadStrategy(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.strategy = ProjectFilesDownloadStrategy()
        self.reports_dir = tempfile.mkdtemp()
        self.page = MagicMock()
        self.page.goto = AsyncMock()
        self.page.wait_for_load_state = AsyncMock()
        self.page.wait_for_selector = AsyncMock()
        self.page.click = AsyncMock()
        self.page.is_visible = AsyncMock(return_value=True)
        # default: grid row-count locator returns 10 rows
        self.page.locator = MagicMock(return_value=_locator(count=10))

    # ---- orchestration ----

    @patch.object(ProjectFilesDownloadStrategy, "_go_to_page", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_download_one", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_row_code", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_read_total", new_callable=AsyncMock)
    async def test_iterates_all_pages(self, m_total, m_code, m_one, m_go):
        m_total.return_value = 20
        m_code.return_value = "PJ 1"
        m_one.return_value = True
        m_go.side_effect = [True, False]  # page1 -> page2 -> stop

        result = await self.strategy.download(self.page, self.reports_dir)

        self.assertTrue(result)
        self.assertEqual(m_one.call_count, 20)  # 10 rows x 2 pages

    @patch.object(ProjectFilesDownloadStrategy, "_go_to_page", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_download_one", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_row_code", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_read_total", new_callable=AsyncMock)
    async def test_respects_limit(self, m_total, m_code, m_one, m_go):
        m_total.return_value = 370
        m_code.return_value = "PJ 1"
        m_one.return_value = True
        m_go.return_value = True  # more pages always available
        self.strategy.limit = 3

        result = await self.strategy.download(self.page, self.reports_dir)

        self.assertTrue(result)
        self.assertEqual(m_one.call_count, 3)
        m_go.assert_not_called()  # limit hit before advancing pages

    @patch.object(ProjectFilesDownloadStrategy, "_go_to_page", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_download_one", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_row_code", new_callable=AsyncMock)
    @patch.object(ProjectFilesDownloadStrategy, "_read_total", new_callable=AsyncMock)
    async def test_skips_existing_files(self, m_total, m_code, m_one, m_go):
        m_total.return_value = 1
        m_code.return_value = "PJ 1"
        m_go.return_value = False
        self.page.locator = MagicMock(return_value=_locator(count=1))
        # pre-create the PDF so the project is treated as already downloaded
        sub = os.path.join(self.reports_dir, "project_files")
        os.makedirs(sub, exist_ok=True)
        open(os.path.join(sub, "PJ_1.pdf"), "w").close()

        result = await self.strategy.download(self.page, self.reports_dir)

        self.assertTrue(result)
        m_one.assert_not_called()  # existing file -> no modal/download

    async def test_download_returns_false_when_list_unavailable(self):
        self.page.goto = AsyncMock(side_effect=Exception("boom"))
        result = await self.strategy.download(self.page, self.reports_dir)
        self.assertFalse(result)

    # ---- single project download ----

    async def test_download_one_saves_pdf(self):
        download = MagicMock()
        download.suggested_filename = "Projeto.pdf"
        download.save_as = AsyncMock()
        self.page.expect_download = MagicMock(return_value=FakeDownloadInfo(download))
        self.page.locator = MagicMock(return_value=_locator(count=1))

        ok = await self.strategy._download_one(self.page, 0, "PJ 9760", self.reports_dir)

        self.assertTrue(ok)
        download.save_as.assert_awaited_once()
        dest = download.save_as.await_args.args[0]
        self.assertEqual(os.path.basename(dest), "PJ_9760.pdf")

    async def test_download_one_skips_when_no_files(self):
        self.page.expect_download = MagicMock()
        self.page.locator = MagicMock(return_value=_locator(count=0))

        ok = await self.strategy._download_one(self.page, 0, "PJ 9999", self.reports_dir)

        self.assertFalse(ok)
        self.page.expect_download.assert_not_called()


if __name__ == "__main__":
    unittest.main()
