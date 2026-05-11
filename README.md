# 🤖 AI Resume Screening System

An end-to-end AI-powered resume screening and candidate analysis system built with Python, LangChain, ChromaDB, and Groq/Llama 3. The system semantically matches resumes to job descriptions and generates professional recruiter reports.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Pipeline Architecture](#pipeline-architecture)
- [API Reference](#api-reference)
- [Known Limitations](#known-limitations)

---

## Overview

Traditional ATS systems use keyword matching, which misses semantically equivalent skills. For example, a resume saying "built neural networks with deep learning frameworks" won't match a job description asking for "PyTorch experience" using keyword search.

This system uses **semantic embeddings** and **retrieval-augmented generation (RAG)** to match candidates based on meaning, not just words. A recruiter uploads resumes, enters a job description, and receives AI-generated analysis with ranked candidates, match scores, and hiring recommendations.

---

## ✨ Features

- **Multi-format ingestion** — PDF, DOCX, and TXT resume support
- **NLP-powered parsing** — extracts name, email, phone, GitHub, LinkedIn, skills, experience, and education
- **Semantic chunking** — splits resumes intelligently using `RecursiveCharacterTextSplitter`
- **Vector search** — stores and retrieves resume chunks using ChromaDB and `all-MiniLM-L6-v2` embeddings
- **LLM analysis** — generates match scores (0–100), strengths, missing skills, and hiring recommendations via Groq/Llama 3
- **Candidate ranking** — sorts candidates by match score automatically
- **JSON export** — saves full screening results with timestamps
- **Streamlit UI** — clean recruiter-facing interface with file upload and results dashboard

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.10+ |
| LLM | Groq API / Llama 3.3-70b |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | ChromaDB |
| NLP | spaCy (en_core_web_sm) |
| Document Parsing | PyPDF, python-docx |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| UI | Streamlit |
| Environment | python-dotenv |

---

## 📁 Project Structure

```
resume_screener/
│
├── data/
│   ├── raw/              ← uploaded resumes
│   └── samples/          ← test resumes for development
│
├── src/
│   ├── ingestion/
│   │   └── loader.py     ← Phase 1: load PDF, DOCX, TXT
│   │
│   ├── preprocessing/
│   │   └── parser.py     ← Phase 2: clean, NER, regex extraction
│   │
│   ├── chunking/
│   │   └── splitter.py   ← Phase 3: chunking strategies
│   │
│   ├── embeddings/
│   │   └── vectorstore.py ← Phase 4: embed + store in ChromaDB
│   │
│   ├── matching/
│   │   └── engine.py     ← Phase 5: JD matching + scoring
│   │
│   └── reporting/
│       └── generator.py  ← Phase 5: LLM report generation
│
├── prompts/
│   └── recruiter_prompt.txt  ← prompt templates
│
├── vectorstore/          ← ChromaDB persists here
├── output/               ← JSON screening results
├── tests/                ← Phase 7 test files
│
├── app.py                ← Streamlit UI entry point
├── config.py             ← paths, model names, chunk settings
├── requirements.txt      ← all dependencies
├── .env                  ← secret keys (never commit)
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/resume_screener.git
cd resume_screener
```

### 2. Create and activate virtual environment

```bash
python -m venv resume
# Windows
resume\Scripts\activate
# Mac/Linux
source resume/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy language model

```bash
python -m spacy download en_core_web_sm
```

### 5. Set up environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)
Get your HuggingFace token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

---

## 🔧 Configuration

All settings live in `config.py`:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL       = "llama-3.3-70b-versatile"
CHUNK_SIZE      = 512
CHUNK_OVERLAP   = 128
```

Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` to tune retrieval quality. Smaller chunks give more precise retrieval; larger chunks give more context per result.

---

## 🚀 Usage

### Run the Streamlit UI

```bash
streamlit run app.py
```

Then:
1. Enter a job title in the sidebar
2. Paste the job description in the left panel
3. Upload one or more resumes (PDF, DOCX, or TXT)
4. Click **Screen Candidates**
5. View ranked results and download the JSON report

### Run the pipeline from command line

```bash
# Test ingestion
python -m src.ingestion.loader

# Test parsing
python -m src.preprocessing.parser

# Test chunking
python -m src.chunking.splitter

# Test vector store
python -m src.embeddings.vectorstore

# Test full engine
python -m src.matching.engine
```

---

## 🏗️ Pipeline Architecture

```
Resume Files (PDF/DOCX/TXT)
        ↓
   Phase 1: Ingestion
   loader.py → raw text + metadata
        ↓
   Phase 2: Preprocessing
   parser.py → structured candidate dict
   (name, email, phone, skills, experience, education)
        ↓
   Phase 3: Chunking
   splitter.py → overlapping text chunks with metadata
   (chunk_size=512, overlap=128)
        ↓
   Phase 4: Embeddings + Vector DB
   vectorstore.py → all-MiniLM-L6-v2 → ChromaDB
        ↓
   Phase 5: AI Matching Engine
   Job Description → embed → semantic search → top K chunks
        ↓
   generator.py → Groq/Llama 3 → structured JSON analysis
   (match_score, strengths, missing_skills, recommendation)
        ↓
   Phase 6: Streamlit UI
   Ranked candidates → download JSON report
```

---

## 📦 Requirements

```
langchain
langchain-community
langchain-text-splitters
pypdf
python-docx
unstructured
spacy
sentence-transformers
chromadb
groq
python-dotenv
streamlit
pydantic
pandas
```

---

## ⚠️ Known Limitations

**PDF extraction quality** — text-based PDFs extract well. Scanned PDFs (image-based) return empty or garbled text. OCR support is not included in this version.

**Name extraction** — spaCy NER struggles with all-caps names common in Indian resumes. The system falls back to the first line of the resume, capped at 4 words.

**Duplicate chunks** — screening the same resume multiple times adds duplicate chunks to ChromaDB. Use the "Clear Vector Store" button in the sidebar before re-screening.

**Single collection** — all resumes share one ChromaDB collection named `resumes`. For multi-tenant or role-specific screening, separate collections per job role are recommended.

**Experience detection** — fresher resumes with no explicit "X years" mention default to 0 years. The system detects "fresher/intern" keywords as a fallback.

**LLM consistency** — match scores may vary slightly between runs due to LLM temperature. Set `temperature=0.0` in `generator.py` for fully deterministic scoring.

---

## 👨‍💻 Author

Built as a learning project to deeply understand:
- Generative AI systems
- RAG (Retrieval-Augmented Generation) pipelines
- Semantic embeddings and vector databases
- NLP preprocessing pipelines
- Production AI architecture

---

## 📄 License

MIT License — free to use and modify.
