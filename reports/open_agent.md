# [Open Agent Platform](https://docs.oap.langchain.com/)

## What it is
A no-code, web-based platform for creating, managing, and orchestrating LangGraph agents. OAP is open source and can be self-hosted or run in the cloud.

## API Access
Provides RESTful API endpoints for:
- Agent creation
- Configuration
- Metadata retrieval
- Runtime management

You can extract agent IDs, config, metadata, logs, execution status, and more.

## Key Features
- Agent management (create, update, delete, list)
- Access to all agent metadata and configuration
- Multi-agent orchestration and supervision
- RAG and external tool integration
- Authentication and access control

## Documentation
- OAP Docs  
- Quickstart & API Reference  
- Agent Setup  

**Open Source:** Yes

---

## API Endpoints

| Endpoint       | Method | Purpose                                   |
|----------------|--------|-------------------------------------------|
| `/info`        | GET    | Metadata about deployment/project/tenant  |
| `/config`      | GET    | Retrieve agent config/schema              |
| `/config`      | PUT    | Update agent config                       |
| `/invoke` or `/run` | POST | Send message/input to agent, get response |
| `/chat`        | POST   | (If chat-based) Chat with agent           |
| `/tools`       | GET    | List available tools                      |
| `/rag`         | GET    | Retrieve or update RAG config             |

---

## Key Distinctions

| Feature                  | LangGraph (Framework)                  | Open Agent Platform (OAP)                       |
|--------------------------|----------------------------------------|------------------------------------------------|
| User Interface           | Code-based (Python/JS)                | No-code, browser-based UI                      |
| Target User              | Developers, engineers                 | Non-technical users, business teams            |
| Agent Creation           | Manual coding, config files           | Visual builder, drag-and-drop, forms           |
| Deployment               | Self-managed, code deployment         | 1-click deployment, managed via UI             |
| Multi-Agent Support      | Yes, via code                         | Yes, via Supervisor UI                         |
| Tool Integration         | Code integration                      | UI-based tool connection (MCP, RAG)            |
| Authentication           | Custom, code-based                    | Built-in (Supabase, JWT, etc.)                 |
| Extensibility            | Full, but requires code               | UI-driven, with code extensibility             |
| Open Source              | Yes                                   | Yes                                            |

---

## Summary Table: OAP vs. LangGraph

| Aspect         | LangGraph (Framework)         | Open Agent Platform (OAP)                         |
|----------------|-------------------------------|--------------------------------------------------|
| Who Uses It    | Developers, AI engineers       | Business users, non-coders, devs                 |
| How It’s Used  | Code, scripts, config files    | Visual UI, drag-and-drop, forms                  |
| Purpose        | Build custom agent systems     | Democratize agent creation, rapid prototyping    |
| Deployment     | Manual, code-based             | 1-click, managed via web UI                      |
| Extensibility  | Full, but technical            | UI-driven, with code hooks                       |

---

## Enterprise Readiness

OAP is enterprise-ready and actively marketed for enterprise automation, with features and documentation supporting production-scale, secure deployments.  
**Note:** As of now, there is no direct, public evidence of specific named enterprises using OAP in production, though all technical and marketing signals indicate it is designed for such use.
