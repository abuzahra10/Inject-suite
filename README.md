# Prompt Injection Attack Generator

This workspace contains a FastAPI backend and a React + TypeScript frontend for generating
indirect prompt injection attacks against PDF documents. The tool accepts a PDF, embeds an
invisible payload inside the first page, and returns the modified document. A placeholder tab for
future defense testing is included in the UI.

## Structure

```
backend/   # FastAPI service and attack logic
frontend/  # React + TypeScript application (Vite)
docs/      # Reference papers
Backup trial/  # Snapshot of the previous implementation
```

## Backend Quickstart

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

## Frontend Quickstart

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies API requests to `http://127.0.0.1:8000`.

## Tests

Backend unit tests live under `backend/tests` and can be executed with:

```bash
cd backend
pytest
```

## Notes

- Only PDF uploads are supported in this iteration.
- The defense tab in the frontend is reserved for future work; no backend endpoints are exposed for defenses yet.
- Earlier experimental code is archived inside `Backup trial/` for reference.
