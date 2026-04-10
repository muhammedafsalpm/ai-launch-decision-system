# War Room Multi-Agent System

## 📋 Overview
A production-ready multi-agent system that simulates a cross-functional "war room" during a product launch. The system analyzes metrics and user feedback to produce a structured launch decision: **Proceed / Pause / Roll Back**. Built with an Orchestrator pattern and exposed via both a Command Line Interface (CLI) and a FastAPI REST API.

## 🏗️ Architecture
```
Input Data → Data Analyst → Marketing Agent → PM Agent → Risk Agent → Final Decision
```

### Agents
| Agent | Responsibility |
|:---|:---|
| **Data Analyst** | Analyzes metrics, detects anomalies, identifies trends |
| **Marketing Agent** | Assesses sentiment, extracts top user issues |
| **PM Agent** | Defines success criteria, evaluates user impact |
| **Risk Agent** | Challenges assumptions, identifies blind spots |
| **Orchestrator** | Coordinates workflow, produces final decision |

### Tools
| Tool | Purpose |
|:---|:---|
| `detect_anomalies()` | Statistical anomaly detection in time-series metrics |
| `compare_trends()` | Multi-metric trend comparison |
| `analyze_sentiment()` | Sentiment distribution analysis |
| `extract_top_issues()` | Keyword-based issue extraction from feedback |

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/muhammedafsalpm/ai-launch-decision-system.git
cd ai-launch-decision-system
```

### 2. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure LLM Provider

**Option A: OpenAI (Cloud)**
```bash
cp .env.example .env
# Edit .env and set:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your-key-here
```

**Option B: Ollama (Local)**
```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3.2

cp .env.example .env
# Edit .env and set:
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3.2
```

### 4. Run the System

The system supports two execution environments: CLI and REST API.

**Mode A: CLI Execution**
Run the orchestration flow on local files directly from the terminal.
```bash
python main.py
```

**Mode B: REST API Execution**
Launch the FastAPI server to expose endpoints for the war room multi-agent simulation.
```bash
python api.py
```
*Interactive API Swagger documentation is available at `http://127.0.0.1:8000/docs`*

### 5. View Output

**For CLI:**
Results are saved locally in the `output/` directory as JSON files:
```bash
cat output/AI_ML_Engineer_[YourName]_April2026.json
```

**For API:**
You can interact with the API endpoints dynamically. For example, upload existing mock datasets via `curl`:
```bash
curl -X POST "http://127.0.0.1:8000/analyze/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "metrics_file=@data/metrics.json" \
  -F "feedback_file=@data/feedback.json" \
  -F "release_notes_file=@data/release_notes.txt"
```

## 📊 Input Data Structure

### `data/metrics.json`
14 days of time-series metrics including:
- DAU (Daily Active Users)
- Error Rate
- Latency (p95)
- Adoption Rate
- Crash Rate
- Support Tickets

### `data/feedback.json`
25-30 user feedback entries with sentiment classification.

### `data/release_notes.txt`
Feature description and known issues.

## 🌐 REST API Endpoints

- `GET /`: Retrieve base API information and available routes.
- `GET /health`: Health check endpoint reflecting current LLM provider and API status.
- `POST /analyze`: Submit structured evaluation targets (metrics, feedback lists) directly via JSON body payload.
- `POST /analyze/upload`: Pass metrics, feedback, and release notes via multipart form file uploads to trigger agent evaluations.

## 📤 Output Format
```json
{
  "decision": "PAUSE",
  "rationale": "Key drivers with metric references...",
  "risk_register": [
    {"risk": "...", "mitigation": "..."}
  ],
  "action_plan": [
    {"action": "...", "owner": "...", "timeline": "..."}
  ],
  "communication_plan": {
    "internal": "...",
    "external": "..."
  },
  "confidence_score": 0.85,
  "confidence_increase_condition": "..."
}
```

## 🔧 Environment Variables

| Variable | Description | Required For |
|:---|:---|:---|
| `LLM_PROVIDER` | `openai` or `ollama` | Always |
| `OPENAI_API_KEY` | OpenAI API key | OpenAI |
| `OPENAI_MODEL` | Model name (default: gpt-4o-mini) | OpenAI |
| `OLLAMA_BASE_URL` | Ollama server URL | Ollama |
| `OLLAMA_MODEL` | Ollama model name | Ollama |

## 📝 Traceability
All agent actions and tool calls are logged to console with `[TRACE]` prefix.

