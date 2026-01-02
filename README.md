AI Resume Analyzer with Local LLM + RAG + ATS Optimization

Good. This is the **right ambition** — but I’m not going to dump chaos on you.


You asked for **all four**, so I’ll give you **all four**, **in the correct order**, with **clean, production-grade structure**.
This is how a real engineer would evolve the project.

---

# STEP 1️⃣ — Add GPT ↔ LLaMA Toggle (Clean, Explicit, Optional)

### Goal

- Default: **LLaMA 3.2 (free, local)**
- Optional: **GPT (paid, only if key exists)**
- ZERO code duplication
- ONE switch

---

## 1.1 Create a config file

### `config.py`

```python
import os

USE_GPT = os.getenv("USE_GPT", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

- Default → LLaMA
- If user sets `USE_GPT=true` + API key → GPT activates

---

## 1.2 Create a single LLM factory (this is key)

### `llm_factory.py`

```python
from config import USE_GPT, OPENAI_API_KEY

def get_llm(temperature=0.2):
    if USE_GPT and OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o",
            temperature=temperature,
            api_key=OPENAI_API_KEY
        )
    else:
        from langchain_community.llms import Ollama
        return Ollama(
            model="llama3.2",
            temperature=temperature
        )
```

👉 **Everywhere in code → use `get_llm()`**

No conditionals. No mess.

---

## 1.3 Update your agent to use the factory

In `agent.py`:

```python
from llm_factory import get_llm
```

Replace:

```python
llm = self.get_llm()
```

With:

```python
llm = get_llm()
```

That’s it.

---

### ✅ Result

- Free by default
- GPT available when needed
- No rewrites later
- Recruiter-friendly design

---

# STEP 2️⃣ — Optimize Prompts (Resume Quality Upgrade)

Your logic is solid.
Your **prompts were the weak point**.

We fix that now.

---

## 2.1 Centralize prompts (non-negotiable)

### `prompts.py`

```python
SKILL_EXTRACTION_PROMPT = """
Extract a clean list of technical and professional skills from the job description.
Rules:
- No explanations
- No duplicates
- Use industry-standard names
- Return ONLY a Python list

Job Description:
{jd}
"""

RESUME_SCORING_PROMPT = """
Evaluate how clearly the resume demonstrates proficiency in {skill}.
Rules:
1. Start with a number from 0–10
2. Then give ONE sentence justification
3. Base judgment ONLY on resume evidence
"""

RESUME_REWRITE_PROMPT = """
Rewrite the resume to be ATS-optimized and recruiter-ready.

Rules:
- Quantify achievements
- Use strong action verbs
- Preserve truthfulness
- Do NOT invent experience
- Optimize for {target_role}

Resume:
{resume}
"""
```

---

## 2.2 Why this improves quality

- Less hallucination
- Better consistency
- Stronger ATS alignment
- GPT & LLaMA both behave better

---

# STEP 3️⃣ — Refactor into Services (Clean Architecture)

Right now your agent is doing **too much**.

We split responsibilities **without overengineering**.

---

## Final Folder Structure (Professional)

```
ai_resume_agent/
│
├── agent.py                # Orchestrator only
├── llm_factory.py          # GPT ↔ LLaMA toggle
├── prompts.py              # All prompts
├── config.py               # Env config
│
├── services/
│   ├── parser.py           # PDF/TXT extraction
│   ├── embeddings.py       # Vector store creation
│   ├── analysis.py         # Skill scoring logic
│   ├── improvement.py     # Resume rewriting
│
├── frontend/
│   └── app.py              # Streamlit UI
│
└── README.md
```

---

## What `agent.py` becomes (important)

`agent.py` should **NOT contain logic**.

It should only:

- call services
- pass data
- return results

That’s how **maintainable systems** are built.

---

# STEP 4️⃣ — README + Demo Story (Recruiter Weapon)

This is where most people fail.
We won’t.

---

## 4.1 README Structure (copy this)

### 🔹 Project Title

**AI-Powered Resume Analyzer (Local-First, Privacy-Safe)**

---

### 🔹 Problem

- Resume screening is opaque
- ATS filters reject good candidates
- Generic advice lacks context

---

### 🔹 Solution

An AI system that:

- Analyzes resumes semantically
- Matches them against job descriptions
- Scores skills transparently
- Suggests targeted improvements
- Runs **locally without API keys**

---

### 🔹 Architecture

- **LLM**: LLaMA 3.2 (Ollama) / GPT-4o (optional)
- **Embeddings**: HuggingFace (local)
- **RAG**: FAISS
- **UI**: Streamlit

---

### 🔹 Key Features

- Resume ↔ JD skill matching
- Numeric scoring with reasoning
- Weakness & improvement detection
- Resume rewriting (ATS optimized)
- Offline-first AI (privacy focused)

---

### 🔹 Why This Is Different

- No API dependency
- No hidden scoring
- No black-box advice
- Recruiter & candidate friendly

---

### 🔹 Demo Flow (THIS IS GOLD)

1. Upload resume
2. Paste JD
3. View skill scorecard
4. See missing skills
5. Generate improved resume
6. Ask follow-up questions

---

### 🔹 How to Run

```bash
ollama serve
streamlit run frontend/app.py
```

---

## 4.2 What to say in interviews (memorize this)

> “I built a resume analysis system that runs locally using open-source LLMs.
> It performs semantic skill matching, transparent scoring, and ATS-aware resume rewriting.
> The system supports GPT optionally but defaults to privacy-first local inference.”

That sentence alone puts you **above 90% of candidates**.

---
