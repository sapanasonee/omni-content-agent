# Omni Content Agent — ADK Multi-Agent Backend

Python multi-agent system built with Google's **Agent Development Kit (ADK)**. This is the orchestration brain for [Omni Content Agent](https://github.com/sapanasonee/omni-content-web) — a content generation platform that learns each founder's voice via persona-scoped RAG.

## 🔗 Live Demo

The full user-facing product is live at: **https://omni-content-web-441385652994.us-central1.run.app**

The ADK API itself is deployed at: `https://omni-content-agent-441385652994.us-central1.run.app` (no root endpoint — accessed via the frontend or `adk` CLI).

## Agent Architecture

Four specialized ADK agents coordinated by an orchestrator:

| Agent | Responsibility | Grounding |
|---|---|---|
| **`orchestrator`** | Routes requests to sub-agents based on intent | — |
| **`brand_dna_agent`** | Retrieves persona voice context | Vertex AI Search (private RAG, `workspace_id` + `persona_id` filter) |
| **`research_agent`** | Surfaces trending topics filtered by brand context | Google Search (via ADK's `google_search` tool) |
| **`content_agent`** | Synthesizes brand context + research into final content, runs critic check | — |

**Why multi-agent over a single LLM call:** A single prompt produces generic output. This pipeline separates concerns — one agent knows *who you are* (private RAG), one knows *what's happening now* (live Google Search), one writes, one judges. Output is grounded twice and quality-checked before delivery.

## RAG & Grounding

- **Vertex AI Search datastore:** `omni-content-agent-v2_1780394823768`
- **Documents indexed:** Brand DNA chunks + every approved content piece
- **Filter:** `workspace_id: ANY(...) AND persona_id: ANY(...)` ensures users only retrieve their own context
- **Memory loop:** Approved content is re-indexed back into the datastore, making future generations sharper

## Tech Stack

- **Framework:** Google Agent Development Kit (`google-adk`)
- **LLM:** Gemini 2.5 Flash via Vertex AI
- **RAG:** Vertex AI Search (`google-cloud-discoveryengine`)
- **Grounding:** ADK's built-in `google_search` tool
- **Hosting:** Google Cloud Run (`adk api_server`)

## Repo Structure

```
orchestrator/agent.py      — Routes user requests to sub-agents
brand_dna_agent/agent.py   — Queries Vertex AI Search with persona filter
research_agent/agent.py    — Trending topic research with Google Search grounding
content_agent/agent.py     — Final content synthesis + critic check
brand_dna.txt              — Sample brand context loaded by research agent
Procfile                   — Cloud Run entrypoint
requirements.txt           — Python dependencies
```

## Local Development

```bash
pip install -r requirements.txt
adk web
```

ADK Web UI runs at `http://localhost:8000`. Select the `orchestrator` agent and send any content brief to see the multi-agent pipeline execute.

## Deployment

Deployed to Google Cloud Run:

```bash
gcloud run deploy omni-content-agent --source . --region us-central1 --allow-unauthenticated
```

The `Procfile` runs `adk api_server --port 8080 --host 0.0.0.0`.

## Submitted to

Google for Startups AI Challenge — June 2026