# JanSetu AI 🇮🇳

> **From Citizen Voice to Government Action**

**JanSetu AI** is an AI-powered citizen feedback and development intelligence platform designed to transform citizen development requests into structured, actionable insights for government decision-makers.

It enables citizens to report local development needs through **voice or text**, processes those requests using AI, stores them as structured governance data, and presents them through separate **Citizen** and **Government** dashboards.

---

## 🎯 Problem

Citizen development requests are often fragmented across different channels such as portals, phone calls, offices, and informal communication.

This can make it difficult to:

- Consolidate citizen feedback into one system
- Identify areas with repeated or concentrated needs
- Understand infrastructure gaps
- Connect citizen demand with demographic and investment context
- Prioritize development requirements transparently
- Measure the potential impact of proposed interventions

---

## 💡 Our Solution

JanSetu AI creates a bridge between **citizen voices and government planning**.

### High-level flow

```text
Citizen
   │
   ├── Voice / Text
   │
   ▼
JanSetu AI
   │
   ├── Speech-to-Text
   ├── Language Detection
   ├── Translation / Normalization
   ├── Issue Classification
   ├── Location Extraction
   └── Urgency Understanding
   │
   ▼
Structured Governance Data
   │
   ├── Citizen Demand
   ├── Infrastructure Context
   ├── Population Context
   ├── Investment Context
   └── Priority Score
   │
   ▼
Government Dashboard
   │
   ├── Recent Citizen Requests
   ├── Work Status
   ├── Demand Hotspots
   ├── Development Priorities
   └── Decision-Support Insights
```

---

## 👥 Two-Dashboard Architecture

JanSetu AI uses clear role separation.

### 🧑 Citizen Dashboard

Citizens can:

- Raise a development need using **voice or text**
- Communicate in supported languages
- Provide additional information when requested
- Review the AI-understood request
- Confirm before submission
- View submitted requests
- Track request status and history

Example:

> **Citizen:** “हमारे गाँव में पीने का पानी नहीं आता।”

JanSetu processes the request and can identify information such as:

```text
Issue       → Drinking Water
Category    → Water / Infrastructure
Location    → Village / Area
Urgency     → Determined from the request
Language    → Hindi
Status      → Submitted
```

If important information such as the village or area is missing, the system can ask a follow-up question before submission.

---

### 🏛️ Government Dashboard

Government users receive structured requests through a separate operational dashboard.

The dashboard provides:

- **Recent Citizen Requests**
- Pending work
- In-progress work
- Completed work
- High-risk / urgent requests
- Demand hotspots
- Development priority rankings
- Estimated population potentially affected
- Area-wise request information
- Supporting analytics
- AI-assisted policy recommendations

The government dashboard does **not** contain citizen submission controls.

---

## 🤖 AI-Powered Processing

AI is used where language understanding is required.

The AI layer can assist with:

1. **Voice understanding**
2. **Language detection**
3. **Translation and normalization**
4. **Issue classification**
5. **Location extraction**
6. **Urgency understanding**
7. **Structured request generation**
8. **Recommendation wording**

The backend remains responsible for deterministic operations such as:

- Database storage
- Request counting
- Aggregation
- Priority calculation
- Population estimation
- Hotspot calculation
- Work-status management

### Design principle

> **AI understands the citizen. Backend applies the rules. Government makes the decision.**

JanSetu AI is intended as **decision-support**, not as a replacement for government decision-makers.

---

## 📊 Transparent Priority Scoring

To avoid treating AI output as the final decision, JanSetu can calculate a transparent development priority score using defined factors.

| Factor | Weight |
|---|---:|
| Citizen Demand | 35% |
| Infrastructure Gap | 25% |
| Population Impact | 20% |
| Urgency | 10% |
| Investment Gap | 10% |
| **Total** | **100%** |

This approach makes the prioritization process easier to explain and audit.

### Example

If multiple citizens report the same infrastructure problem in an area with a significant infrastructure gap and high population impact, the area can receive a higher priority score.

---

## 🗺️ Demand Hotspots

JanSetu can identify locations where similar development requests are concentrated.

For example:

```text
Area A
├── 48 Water Requests
├── High Infrastructure Gap
├── Large Population Context
└── High Priority

Area B
├── 12 Road Requests
├── Medium Infrastructure Gap
├── Moderate Population Context
└── Medium Priority
```

Hotspot analysis helps decision-makers move from looking at individual complaints to understanding **area-level development demand**.

---

## 👨‍👩‍👧 Population Impact

JanSetu can estimate the number of people potentially affected by a development issue using structured demographic and location data.

The dashboard should present this as:

> **~25,000 potentially affected**

rather than claiming that the number is a confirmed real-world measurement.

---

## 🏗️ Work Management

Government users can track the lifecycle of requests using statuses such as:

```text
PENDING
   ↓
IN_PROGRESS
   ↓
COMPLETED
```

Other possible states include:

```text
ON_HOLD
CANCELLED
```

The system can also support information such as:

- Assigned officer / team
- Progress percentage
- Government notes
- Completion notes
- Risk level
- Created timestamp
- Updated timestamp
- Completion timestamp

This allows the citizen-facing status and government work-management state to remain connected through the shared backend database.

---

## 🕒 Request Recency

Citizen requests are stored with a submission timestamp.

Recent requests are ordered using the backend/database so that the newest request appears first:

```text
ORDER BY created_at DESC, id DESC
```

This keeps **recency** separate from **priority**.

For priority-based views, requests can instead be ordered by:

```text
priority_score DESC
created_at DESC
```

---

## 🏛️ Data Architecture

The platform follows a frontend–backend architecture.

```text
React Frontend
      │
      ▼
Python / FastAPI Backend
      │
      ├── AI Services
      │
      ├── Request APIs
      │
      ├── Priority Logic
      │
      └── Database Layer
             │
             ▼
          SQLite
```

The current prototype uses **SQLite for persistent application data**.

Supporting prototype data can represent:

- Demographics
- Infrastructure conditions
- Investment context
- Development/work information

Such supporting data should be clearly identified as **prototype/sample data** unless connected to a verified live source.

---

## 🧩 Technology Stack

### Frontend
- React.js
- JavaScript
- Modern responsive UI

### Backend
- Python
- FastAPI

### AI / NLP
- Multilingual NLP
- Speech-to-Text
- Text classification
- LLM-based language understanding
- Translation / normalization

### Database
- SQLite

### Visualization
- Interactive maps
- Analytics dashboard
- Development priority views

> **Note:** The exact LLM model/version used by a particular deployment should be taken from that deployment's configuration. This README intentionally does not claim a specific model without verified project configuration.

---

## 📁 Project Structure

A simplified view of the application:

```text
JanSetu/
└── artifacts/
    └── jan-setu-ai/
        ├── frontend/
        │   └── ...
        │
        └── backend/
            ├── app/
            │   ├── db.py
            │   ├── services/
            │   │   └── ai.py
            │   └── routes/
            │       └── requests.py
            │
            └── ...
```

The exact structure may evolve as the project is developed.

---

## 🔄 End-to-End Request Flow

### Step 1 — Citizen submits a request

The citizen speaks or types a development problem.

### Step 2 — AI understands the request

The system processes language, identifies the issue, and extracts relevant information.

### Step 3 — Missing information is collected

If required information such as the village or area is missing, JanSetu can ask the citizen a follow-up question.

### Step 4 — Citizen confirms

Before submission, the citizen can review the interpreted request.

### Step 5 — Request is stored

The structured request is saved in the backend database with its timestamp and status.

### Step 6 — Government dashboard refreshes

The government dashboard retrieves requests from the shared backend database.

### Step 7 — Analytics and prioritization

The backend calculates demand, priority, impact, and other decision-support indicators.

### Step 8 — Government takes action

Government users can review, assign, update, and complete development work.

---

## 🔐 Data Principles

JanSetu is designed around the following principles:

- **Role separation** — citizen and government workflows remain distinct
- **Structured data** — natural-language requests become structured governance records
- **Traceability** — requests retain their original citizen input and processed representation
- **Transparent prioritization** — priority factors and weights are defined explicitly
- **AI-assisted, human-led decisions** — AI supports analysis; government officials make decisions
- **Prototype transparency** — sample supporting data is not presented as live government data

Where applicable, request records can retain:

```text
original_text
original_language
english_translation
category
issue
location
urgency
status
user_id
created_at
```

---

## 🌐 Multilingual Citizen Experience

JanSetu is designed around a multilingual citizen experience, especially for users who may find complex digital forms difficult to use.

The intended interaction is:

```text
Citizen's Preferred Language
          ↓
Speech / Text
          ↓
Language Detection
          ↓
Translation / Normalization
          ↓
AI Understanding
          ↓
Structured Governance Request
```

Language support should only be advertised for languages that are actually implemented and tested in the deployed version.

---

## 🧪 Prototype Status

JanSetu AI is a **prototype / hackathon implementation**.

The original concept proposes integration with demographic, infrastructure, and investment data and a government-facing analytics layer. The prototype is **not presented as being connected to live government systems or APIs**.

Therefore:

- Citizen requests submitted through the application can be real application records.
- Supporting demographic/infrastructure/investment information may be prototype/sample data.
- Dashboard estimates are decision-support indicators, not official government statistics.
- Priority recommendations are not final government decisions.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Prashant004425/JanSetu.git
cd JanSetu
```

### 2. Go to the application

```bash
cd artifacts/jan-setu-ai
```

### 3. Backend setup

Create and activate a Python virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

### 4. Start the backend

Use the backend start command/configuration provided by the project.

For FastAPI development, this commonly follows the pattern:

```bash
uvicorn app.main:app --reload
```

> If the project's current entry point differs, use the command defined in the repository configuration.

### 5. Start the frontend

Install dependencies:

```bash
npm install
```

Then start the development server using the project's configured command, for example:

```bash
npm run dev
```

---

## 🔗 Repository

**GitHub:**  
https://github.com/Prashant004425/JanSetu

---

## 🌟 Key Highlights

| Capability | JanSetu AI |
|---|---|
| Citizen voice input | ✅ |
| Citizen text input | ✅ |
| AI request understanding | ✅ |
| Multilingual processing | Designed for |
| Follow-up questions | ✅ |
| Citizen confirmation | ✅ |
| Shared backend database | ✅ |
| Government request dashboard | ✅ |
| Request status tracking | ✅ |
| Demand hotspot analysis | ✅ |
| Transparent priority scoring | ✅ |
| Population impact estimation | ✅ |
| Government work management | ✅ |
| Live government API integration | ❌ Prototype |
| AI as final decision-maker | ❌ |

---

## 🌍 Impact

JanSetu AI aims to make public-development planning more **citizen-centric, data-driven, transparent, and accessible**.

Instead of treating citizen feedback as isolated complaints, the platform turns it into structured information that can help identify:

- What citizens need
- Where the need is concentrated
- How urgent the issue may be
- What infrastructure gaps exist
- How many people may potentially be affected
- Which development areas may deserve greater attention

> **JanSetu AI transforms fragmented citizen feedback into actionable intelligence, helping policymakers make more informed development decisions.**

---

## 🔮 Future Scope

Potential future improvements include:

- Integration with verified government data sources
- Secure government API integration
- More regional Indian language support
- Better speech recognition for regional accents
- Advanced geospatial hotspot detection
- Real-time infrastructure datasets
- More detailed development-impact analytics
- Government authentication and role-based access control
- Audit logs and approval workflows
- Mobile-first citizen experience
- WhatsApp and other messaging-channel integration
- Production-grade scalability and monitoring

---

## 👨‍💻 Team — NexGen

Built for the **AI for Digital Public Infrastructure & Governance** theme.

**Team Members**
- Ankita Anand
- Prashant Kumar Pandey
- Amisha Kumari

---

## 📜 Disclaimer

JanSetu AI is a prototype created to demonstrate an AI-assisted citizen feedback and development intelligence workflow.

It should not be interpreted as an official government platform, official government dataset, or a replacement for government decision-making.

**AI assists with understanding and analysis. Final development decisions remain with authorized government decision-makers.**

---

### 🇮🇳 From Citizen Voice → Data → Action

**Every Citizen Voice Matters.**
