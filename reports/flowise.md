# Flowise

## What it is
An open-source, visual AI agent builder supporting LangGraph, LangChain, and other frameworks. Flowise offers a drag-and-drop interface and robust API access.

| Framework  | Native Support in Flowise? | Notes                                                                 |
|------------|-----------------------------|-----------------------------------------------------------------------|
| LangChain  | Yes                         | Full integration, visual builder, agent and chain support            |
| LangGraph  | No (as of July 2025)        | No direct/native support; some “graph-style” workflows possible via Flowise’s own tools |


## API Access
Exposes endpoints for creating, updating, and retrieving agent configurations, metadata, and runtime data. You can programmatically manage agents and extract all relevant details.

## Key Features
- Visual builder for single and multi-agent systems
- API, SDK, and CLI for automation and integration
- Access to agent config, logs, execution status, and more
- Self-hosted and cloud deployment options
- Supports advanced orchestration, RAG, and tool integration

## Documentation
- Flowise Docs  
- API Usage  

**Open Source:** Yes

---

## Flowise: Endpoints for Retrieving LangGraph Agent Config & Metadata

Flowise provides a robust set of REST API endpoints and tools that allow you to programmatically access, manage, and extract configuration and metadata for LangGraph-based agents.

### 1. Core API Endpoints for Agent Management

| Endpoint                          | Method | Description                                                               |
|-----------------------------------|--------|---------------------------------------------------------------------------|
| `/api/v1/flows`                   | GET    | List all flows (agent workflows) and their metadata                      |
| `/api/v1/flows/{flowId}`         | GET    | Retrieve full configuration and metadata for a specific agent/flow       |
| `/api/v1/flows/{flowId}`         | PUT    | Update agent/flow configuration                                          |
| `/api/v1/flows/{flowId}`         | DELETE | Delete an agent/flow                                                     |
| `/api/v1/flows`                   | POST   | Create a new agent/flow                                                  |
| `/api/v1/prediction/{flowId}`    | POST   | Execute an agent/flow and retrieve run metadata, logs, and outputs       |

**Agent/Flow Metadata:**  
Each flow (agent) includes unique identifiers, name, description, tags, creation/update timestamps, owner, and configuration details such as nodes, tools, and parameters.

**Run Metadata:**  
When executing a flow, you can retrieve run-specific data including run ID, status, logs, errors, and dynamic input/output.

---

### 2. Agent Node and Tool Configuration

**Agent Node Configuration Includes:**
- Name, description, and tool assignments
- Model parameters (e.g., LLM model, temperature)
- Memory and state management options
- Knowledge/document store connections
- Input/output variable mappings

**Tool Configuration Includes:**
- Endpoint URL
- Input/output schema (JSON schema for parameters and body)
- Headers and authentication
- Descriptions and usage notes

---

### 3. OpenAPI Toolkit for Bulk API Integration

**Purpose:**  
Import an OpenAPI YAML file to auto-generate tools for each API endpoint, making all API operations available as agent tools.

**Configuration:**  
Specify the YAML file, headers, and custom code for response handling.

**Metadata Extraction:**  
Each imported tool exposes its endpoint, method, input/output schema, and description.

---

### 4. Example: Retrieving Agent Config and Metadata

**List All Agents/Flows:**  
`GET /api/v1/flows`  
Returns a list of all agent flows with summary metadata.

**Get Specific Agent/Flow Config:**  
`GET /api/v1/flows/{flowId}`  
Returns the full configuration, including nodes, tools, parameters, and metadata.

**Execute Agent and Get Run Metadata:**  
`POST /api/v1/prediction/{flowId}`  
Returns run ID, status, logs, errors, and outputs for a specific execution.

---

### 5. Additional Features

- **Variables and State:** Flows can use static and runtime variables, which are accessible via the API and included in the flow configuration.
- **Environment and Database:** Flowise supports configuration via environment variables and can store agent metadata in various databases for enterprise use.

---

## Summary Table: Key Endpoints

| Endpoint                       | Method | Returns/Action                                      |
|--------------------------------|--------|-----------------------------------------------------|
| `/api/v1/flows`               | GET    | List of all agents/flows with metadata              |
| `/api/v1/flows/{flowId}`      | GET    | Full config and metadata for a specific agent       |
| `/api/v1/prediction/{flowId}` | POST   | Run agent, get run metadata, logs, outputs          |

---

## Summary Table: Flowise Capabilities for LangGraph Agents

| Capability                     | Supported in Flowise? | How to Access/Configure                       |
|--------------------------------|------------------------|-----------------------------------------------|
| Custom agent creation          | Yes                    | Visual builder, API                           |
| Multi-agent orchestration      | Yes                    | Supervisor/worker nodes, canvas               |
| Tool and API integration       | Yes                    | HTTP node, OpenAPI toolkit                    |
| State, memory, knowledge stores| Yes                    | Node config, document/vector stores           |
| Retrieve config & metadata     | Yes                    | `/api/v1/flows`, `/api/v1/flows/{id}`         |
| Retrieve run logs & outputs    | Yes                    | `/api/v1/prediction/{id}`                     |

---

## Summary Table: Flowise Enterprise Adoption

| Evidence Type         | Details/Examples                                                                |
|------------------------|---------------------------------------------------------------------------------|
| Customer Testimonials | UneeQ, QmicQatar, BTS Digital (senior leaders cite Flowise in production use)   |
| Enterprise Features   | On-premise, SSO/SAML, LDAP/RBAC, audit logs, 99.99% uptime SLA                  |
| Use Cases             | Digital humans, fleet copilots, internal AI assistants, customer support bots   |
| Target Customers      | Enterprises, medium businesses, developers, startups, business analysts         |
| Deployment Options    | Cloud, on-premise, air-gapped, horizontal scaling                               |
