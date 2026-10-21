# Examples

Runnable examples for the two SIGPESQ ETLs. All of them log in **once** and reuse
the same authenticated session (the portal rate-limits logins).

| Script | What it does | Output |
|---|---|---|
| [`run_reports_etl.py`](run_reports_etl.py) | ETL 1 — report files (Excel): groups, projects, advisorships | `reports/research_group/`, `reports/research_projects/`, `reports/advisorships/<year>/` |
| [`run_pdf_etl.py`](run_pdf_etl.py) | ETL 2 — the "Projeto" PDF of every campus project | `reports/project_files/<code>.pdf` |
| [`run_all_etls.py`](run_all_etls.py) | **Both** ETLs in a single login | all of the above |
| [`extract_projects.py`](extract_projects.py) | PDF → JSON via Mistral (text-first, OCR fallback) | `reports/project_files_json/<code>.json` + `projects.json` |
| [`extract_projects_batch.py`](extract_projects_batch.py) | Bulk PDF → JSON via Mistral **Batch API** (~50% cost, async) | same as above |

## Setup

```bash
pip install -e .            # or: export PYTHONPATH=src
cp .env.example .env        # then fill SIGPESQ_USER / SIGPESQ_PASSWORD
```

## Run

```bash
python examples/run_all_etls.py              # both ETLs, one login
python examples/run_all_etls.py --limit 5    # cap the PDF ETL for a quick test
python examples/run_reports_etl.py           # only the Excel reports
python examples/run_pdf_etl.py --limit 5     # only PDFs, first 5 projects
python examples/run_pdf_etl.py --headful     # watch the browser

# PDF -> JSON extraction (needs MISTRAL_KEY in .env, and: pip install -e ".[extract]")
python examples/extract_projects.py --limit 5
```

> ⚠️ **One login only.** Do **not** launch two ETL processes back-to-back — that
> logs in twice and trips the portal's rate limit
> ("Muitas tentativas. Aguarde alguns segundos."). Use `run_all_etls.py`
> (or `python agent.py download-everything`) to run both in a single login.
