# Prompt Injection Attack Generator

This workspace contains a FastAPI backend and a React + TypeScript frontend for generating
indirect prompt injection attacks against PDF documents. The tool accepts a PDF, embeds an
invisible payload inside the first page, and returns the modified document.

**Current Status:** 22 attack recipes across 6 categories, comprehensive test suite, and categorized UI.

## Overview

This tool is designed for security research on **indirect prompt injection attacks** in LLM-based systems. Unlike direct prompt injection where attackers interact with the model directly, indirect attacks embed malicious instructions in documents (PDFs) that are later processed by LLM systems such as:
- Retrieval-Augmented Generation (RAG) pipelines
- Automated document review systems
- Research paper evaluation assistants
- CV/resume screening tools
- Document summarization services

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

## Attack Taxonomy

The system includes **22 distinct attack recipes** organized into 6 categories:

### 1. Context Hijacking (4 attacks)
These attacks attempt to override the system's intended task or role.

- **Preface Hijack** - Classic authority override inserted at the top of the document
- **Role Reversal** - Forces the LLM to abandon its critical role and become supportive
- **Ignore Review** - Emergency distraction technique from "Publish to Perish" paper
- **Task Substitution** - Redirects evaluation task to promotional summarization

### 2. Output Manipulation (6 attacks)
These attacks control what the LLM generates without changing its perceived role.

- **Acceptance Bias** - Role-playing instruction biasing towards acceptance
- **Score Inflation** - Forces numerical scores >= 8/10 regardless of quality
- **Watermark Injection** - Inserts hidden phrase to detect successful injection
- **Homoglyph Marker** - Requests Cyrillic character substitution for detection
- **Sentiment Reversal** - Subtly replaces critical terms with positive ones
- **Novelty Inflation** - Forces inflated novelty assessment with superlatives

### 3. Information Extraction (2 attacks)
These attacks attempt to leak system information or other documents.

- **Prompt Leakage** - Attempts to extract and reveal system instructions
- **Cross-Document Leakage** - Attempts to leak other documents from the session

### 4. Defense Evasion (5 attacks)
These attacks use techniques to bypass detection mechanisms.

- **Delimiter Confusion** - Creates fake document boundaries to confuse parsing
- **Gradual Instruction** - Subtle injection disguised as normal content
- **Base64 Injection** - Encodes instructions to evade keyword detection
- **ROT13 Obfuscated** - ROT13-encoded instructions to evade simple detection
- **XML Injection** - XML tag injection to create fake system context

### 5. RAG-Specific (2 attacks)
These attacks exploit retrieval-augmented generation systems specifically.

- **Retrieval Poisoning** - Poisons vector databases to bias future retrievals
- **Multi-Turn Manipulation** - Persistent attack affecting conversation history

### 6. Domain-Specific (3 attacks)
These attacks target specific application domains (peer review).

- **Reviewer Bias** - Leverages false authority and anchoring bias
- **Citation Authority** - Uses fake citation metrics and journal prestige
- **Methodology Blindspot** - Exploits LLM uncertainty about specialized methods

## Attack Mechanism

All attacks use the same invisible injection technique:
1. **White-on-white text**: RGB(255, 255, 255) text on white background
2. **Tiny font size**: 1.2pt to avoid visual detection
3. **Strategic positioning**: Top, bottom, center, or margin placement
4. **Unicode support**: Handles special characters via DejaVu/FreeSans fonts

The embedded text is invisible to human readers but extracted by LLM systems processing the document.

## Research Applications

This tool enables systematic evaluation of:
- ✅ **Attack Success Rates** - Which attacks work against which LLMs?
- ✅ **Defense Effectiveness** - How well do sanitization/detection methods work?
- ✅ **Transferability** - Do attacks work across different models?
- ✅ **Robustness Testing** - Can systems resist sophisticated evasion techniques?
- ✅ **Category Analysis** - Which attack categories are most/least effective?

## Notes

- Only PDF uploads are supported in this iteration.
- The defense tab in the frontend is reserved for future work; defense code exists but no API endpoints yet.
- Earlier experimental code is archived inside `Backup trial/` for reference.
- All 22 attacks are fully tested with comprehensive unit tests in `backend/tests/`.
- Frontend UI automatically groups attacks by category for easy navigation.
