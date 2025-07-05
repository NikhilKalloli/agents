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



Flowise
What it is:
An open-source, visual AI agent builder supporting LangGraph, LangChain, and other frameworks. Flowise offers a drag-and-drop interface and robust API access.

API Access:
Exposes endpoints for creating, updating, and retrieving agent configurations, metadata, and runtime data. You can programmatically manage agents and extract all relevant details.

Key Features:

Visual builder for single and multi-agent systems

API, SDK, and CLI for automation and integration

Access to agent config, logs, execution status, and more

Self-hosted and cloud deployment options

Supports advanced orchestration, RAG, and tool integration

Documentation:
Flowise Docs
API Usage

Open Source: Yes

Flowise: Endpoints for Retrieving LangGraph Agent Config & Metadata
Flowise provides a robust set of REST API endpoints and tools that allow you to programmatically access, manage, and extract configuration and metadata for LangGraph-based agents. Below is a summary of the key endpoints and mechanisms relevant for retrieving agent details, configuration, and runtime metadata.

1. Core API Endpoints for Agent Management
Endpoint Pattern	Method	Description
/api/v1/flows	GET	List all flows (agent workflows) and their metadata
/api/v1/flows/{flowId}	GET	Retrieve full configuration and metadata for a specific agent/flow
/api/v1/flows/{flowId}	PUT	Update agent/flow configuration
/api/v1/flows/{flowId}	DELETE	Delete an agent/flow
/api/v1/flows	POST	Create a new agent/flow
/api/v1/prediction/{flowId}	POST	Execute an agent/flow and retrieve run metadata, logs, and outputs
Agent/Flow Metadata: Each flow (agent) includes unique identifiers, name, description, tags, creation/update timestamps, owner, and configuration details such as nodes, tools, and parameters.

Run Metadata: When executing a flow, you can retrieve run-specific data including run ID, status, logs, errors, and dynamic input/output.

2. Agent Node and Tool Configuration
Agent Node: Each agent node within a flow can be configured with:

Name, description, and tool assignments

Model parameters (e.g., LLM model, temperature)

Memory and state management options

Knowledge/document store connections

Input/output variable mappings

Tool Configuration: Tools (GET, POST, PUT, DELETE, OpenAPI Toolkit) are defined with:

Endpoint URL

Input/output schema (JSON schema for parameters and body)

Headers and authentication

Descriptions and usage notes

3. OpenAPI Toolkit for Bulk API Integration
Purpose: Import an OpenAPI YAML file to auto-generate tools for each API endpoint, making all API operations available as agent tools.

Configuration: Specify the YAML file, headers, and custom code for response handling.

Metadata Extraction: Each imported tool exposes its endpoint, method, input/output schema, and description.

4. Example: Retrieving Agent Config and Metadata
List All Agents/Flows:
GET /api/v1/flows
Returns a list of all agent flows with summary metadata.

Get Specific Agent/Flow Config:
GET /api/v1/flows/{flowId}
Returns the full configuration, including nodes, tools, parameters, and metadata.

Execute Agent and Get Run Metadata:
POST /api/v1/prediction/{flowId}
Returns run ID, status, logs, errors, and outputs for a specific execution.

5. Additional Features
Variables and State: Flows can use static and runtime variables, which are accessible via the API and included in the flow configuration.

Environment and Database: Flowise supports configuration via environment variables and can store agent metadata in various databases for enterprise use.

6. Summary Table: Key Endpoints
Endpoint	Method	Returns/Action
/api/v1/flows	GET	List of all agents/flows with metadata
/api/v1/flows/{flowId}	GET	Full config and metadata for a specific agent
/api/v1/prediction/{flowId}	POST	Run agent, get run metadata, logs, outputs



Summary Table: Flowise Capabilities for LangGraph Agents
Capability	Supported in Flowise?	How to Access/Configure
Custom agent creation	Yes	Visual builder, API
Multi-agent orchestration	Yes	Supervisor/worker nodes, canvas
Tool and API integration	Yes	HTTP node, OpenAPI toolkit
State, memory, knowledge stores	Yes	Node config, document/vector stores
Retrieve config & metadata via API	Yes	/api/v1/flows, /api/v1/flows/{id}
Retrieve run logs & outputs	Yes	/api/v1/prediction/{id}

Summary Table: Flowise Enterprise Adoption
Evidence Type	Details/Examples
Customer Testimonials	UneeQ, QmicQatar, BTS Digital (senior leaders cite Flowise in production use)
Enterprise Features	On-premise, SSO/SAML, LDAP/RBAC, audit logs, 99.99% uptime SLA
Use Cases	Digital humans, fleet copilots, internal AI assistants, customer support bots
Target Customers	Enterprises, medium businesses, developers, startups, business analysts
Deployment Options	Cloud, on-premise, air-gapped, horizontal scaling

