# 🌿 AyurVani — Multilingual Ayurveda Healthcare Assistant

[![CI/CD](https://github.com/your-org/ayurvani/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/your-org/ayurvani/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> AI-powered multilingual Ayurveda assistant combining voice AI, multimodal understanding, and ancient healing wisdom for personalized healthcare — powered by Amazon Nova.

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│                     React / Mobile Frontend                 │
│  ┌──────────────┐ ┌────────────────┐ ┌───────────────────┐  │
│  │ Voice Console│ │ Symptom Analyzer│ │ Treatment Planner │  │
│  └──────┬───────┘ └───────┬────────┘ └────────┬──────────┘  │
└─────────┼─────────────────┼───────────────────┼─────────────┘
│   HTTPS / WSS   │                   │
┌─────────▼─────────────────▼───────────────────▼─────────────┐
│                   FastAPI  Backend (ECS)                     │
│  ┌────────────┐ ┌──────────────┐ ┌────────────────────────┐ │
│  │ Voice Route│ │Consult Route │ │  Multimodal Route      │ │
│  └─────┬──────┘ └──────┬───────┘ └──────────┬─────────────┘ │
│        │               │                    │               │
│  ┌─────▼───────────────▼────────────────────▼─────────────┐ │
│  │              Agentic Orchestration Layer                │ │
│  │   (Strands Agents  /  LangChain  /  Tool Router)       │ │
│  └─────┬────────────┬──────────────────┬──────────────────┘ │
└────────┼────────────┼──────────────────┼────────────────────┘
│            │                  │
┌────────▼───┐ ┌──────▼──────┐ ┌────────▼──────────┐
│Nova 2 Sonic│ │Nova 2 Lite  │ │Nova Multimodal    │
│ (Voice AI) │ │ (Reasoning) │ │ Embeddings        │
└────────────┘ └─────────────┘ └───────────────────┘
│            │                  │
┌─────▼────────────▼──────────────────▼───┐
│       Amazon OpenSearch (Vector DB)     │
│       DynamoDB  ·  S3  ·  CloudWatch    │
└─────────────────────────────────────────┘

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS CLI configured with Bedrock access
- Docker & Docker Compose

### Local Development

```bash
# Clone
git clone https://github.com/your-org/ayurvani.git
cd ayurvani

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend/web
npm install && npm run dev
```

### Docker

```bash
docker-compose up --build
```

## 📁 Project Structure


ayurvani/
├── backend/          # FastAPI + Agents + Services
├── frontend/         # React web + React Native mobile
├── infrastructure/   # Terraform + CloudFormation
├── data/             # Ayurveda corpus & embeddings
├── notebooks/        # Jupyter analysis notebooks
└── tests/            # Unit, integration, e2e

## 🧠 Nova Models Used

| Model | Purpose |
|-------|---------|
| Nova 2 Sonic | Real-time voice consultations |
| Nova 2 Lite | Ayurvedic reasoning & recommendations |
| Nova Multimodal Embeddings | Semantic search across text, images, audio |

## 🌐 Supported Languages

English · Hindi · Tamil · Telugu · Kannada · Malayalam · Bengali · Marathi · Gujarati · Punjabi · Odia · Urdu · Sanskrit

## ⚠️ Disclaimer

AyurVani provides educational health information based on traditional Ayurvedic principles. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

## 📄 License

MIT © 2025 AyurVani Contributors
