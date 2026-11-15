# shophub-merchant-ai-assistant
AI-powered multi-tenant e-commerce support assistant with secure tenant isolation, order management, customer insights, and refund/cancellation workflows.


# ShopHub – Merchant AI Assistant

An AI-powered multi-agent assistant designed to help merchants manage orders, retrieve business information, and handle refund requests through intelligent conversations.

The application uses **Python, FastAPI, LangGraph, LLMs, and multi-agent orchestration** to provide secure, context-aware merchant operations with human approval for sensitive actions.

---

## 🚀 Key Features

- **Multi-Agent Architecture:** Specialized agents handle different merchant operations.
- **LangGraph Orchestration:** Manages agent execution, workflow transitions, and conversation state.
- **LLM Integration:** Uses Groq API for intelligent natural language understanding and responses.
- **Authentication & Authorization:** Secures APIs using JWT-based authentication.
- **Multi-Tenant Architecture:** Ensures merchants can access only their own data.
- **Order Management:** Retrieve orders, filter orders, and analyze order information.
- **Human-in-the-Loop (HITL):** Requires human confirmation before executing sensitive refund operations.
- **MCP (Model Context Protocol):** Supports structured interaction between AI agents and external tools.
- **A2A Communication:** Enables communication and coordination between specialized AI agents.
- **Streaming Responses:** Delivers assistant responses using Server-Sent Events (SSE).
- **Conversation Memory:** Maintains conversation context using LangGraph checkpointing.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| AI Framework | LangChain |
| Agent Orchestration | LangGraph |
| LLM Provider | Groq API |
| Authentication | JWT |
| Database | SQLite |
| API Communication | REST API |
| Streaming | Server-Sent Events (SSE) |
| Agent Communication | A2A |
| Tool Integration | MCP |
| Testing | Pytest |
| Version Control | Git, GitHub |


---

## 🏗️ System Architecture

The application follows a layered architecture.

```text
             Merchant / Client
                    |
                    |
              FastAPI Backend
                    |
          Authentication & JWT
                    |
          Tenant Authorization
                    |
             API Endpoints
                    |
           LangGraph Workflow
                    |
          Multi-Agent System
                    |
       +------------+------------+
       |            |            |
   Order Agent  Refund Agent  Merchant Agent
       |            |            |
       +------------+------------+
                    |
               AI Tools
                    |
          MCP / A2A Integration
                    |
              Database
                    |
               SQLite
```

### Architecture Components

**1. FastAPI Backend**
- Exposes REST APIs.
- Handles authentication and authorization.
- Provides order management endpoints.
- Streams AI responses to clients.

**2. LangGraph Orchestration**
- Controls the execution flow between agents.
- Maintains conversation state.
- Supports conditional routing.
- Manages human approval workflows.

**3. Multi-Agent System**
- Order Agent: Retrieves and analyzes merchant orders.
- Refund Agent: Prepares and processes refund workflows.
- Merchant Agent: Handles merchant-related queries.

**4. Authentication & Tenant Isolation**
- Validates JWT access tokens.
- Identifies the authenticated merchant.
- Restricts database queries to the authorized merchant.
- Prevents cross-tenant data access.

**5. Human-in-the-Loop**
- Generates refund proposals.
- Pauses execution for human confirmation.
- Resumes the workflow after approval.
- Prevents refund execution without authorization.

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Praveenkumarreddy12/shophub-merchant-ai-assistant.git
```

Navigate to the project directory:

```bash
cd shophub-merchant-ai-assistant
```

### 2. Create a Virtual Environment

Create an isolated Python environment:

**Windows:**

```bash
python -m venv venv
```

**Linux / macOS:**

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

Once activated, your terminal should display:

```text
(venv)
```

### 4. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 5. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./shophub.db
```

Replace the placeholder values with your actual configuration.

**Important:** Never commit your `.env` file or expose API keys in GitHub.

---

## 🔑 Generate Groq API Key

1. Visit https://console.groq.com/
2. Sign in to your account.
3. Navigate to API Keys.
4. Generate a new API key.
5. Add the key to your `.env` file.

---

## ▶️ Running the Application

### Start the FastAPI Server

```bash
uvicorn app.main:app --reload --port 8000
```

If your application entry point is different, update the command accordingly.

### Access API Documentation

Once the server starts, open:

| Resource | URL |
|---|---|
| API Server | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

### Run the Client

If using the Python client:

```bash
python client.py
```

---

## 🔄 Agent Workflow

The application uses LangGraph to orchestrate AI agents.

1. Merchant sends a message.
2. FastAPI receives the request.
3. JWT authentication validates the merchant.
4. Tenant authorization identifies the merchant's data scope.
5. LangGraph processes the message.
6. The appropriate agent is selected.
7. The agent invokes the required tools.
8. Results are returned to the orchestrator.
9. The assistant generates a response.
10. The response is streamed back to the client.

### Example: Order Lookup

```text
Merchant
   |
   v
FastAPI Chat API
   |
   v
JWT Authentication
   |
   v
LangGraph Orchestrator
   |
   v
Order Agent
   |
   v
Order Retrieval Tool
   |
   v
Tenant-Filtered Database
   |
   v
LLM Response
   |
   v
Merchant
```

### Example: Refund Approval Workflow

```text
Merchant Requests Refund
          |
          v
     Refund Agent
          |
          v
   Retrieve Order Details
          |
          v
    Generate Proposal
          |
          v
     Human Approval
          |
      +---+---+
      |       |
    Approve  Reject
      |       |
      v       v
 Execute   Cancel
 Refund    Request
      |
      v
 Confirmation
```

---

## 🧪 Running Tests

The project uses Pytest for automated testing.

Install Pytest if it is not already installed:

```bash
pip install pytest
```

Run all tests:

```bash
pytest
```

Run a specific test:

```bash
pytest tests/test_tenant_isolation.py -v
```

Run tests with detailed output:

```bash
pytest -v -s
```

### Important Test Scenarios

- Authentication validation.
- JWT token verification.
- Merchant authorization.
- Tenant isolation.
- Order retrieval.
- Unauthorized access prevention.
- Refund approval workflow.

---

## 📦 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

To generate or update the requirements file from your active virtual environment:

```bash
pip freeze > requirements.txt
```

To inspect installed dependencies:

```bash
pip list
```

---

## 🔒 Security Considerations

- API access requires authentication.
- JWT tokens are used for identity verification.
- Merchant-specific authorization protects tenant data.
- Refund execution requires explicit human approval.
- Environment variables are used for sensitive credentials.
- Database operations must enforce merchant-level access restrictions.

---

## 🚀 Future Enhancements

- Integrate PostgreSQL for production database management.
- Implement advanced monitoring and logging.
- Add role-based access control (RBAC).
- Integrate additional external merchant services.
- Implement more specialized AI agents.
- Add Docker-based deployment.
- Improve automated integration and load testing.

---

## 👨‍💻 Author

**Praveen Kumar Reddy**

GitHub: https://github.com/Praveenkumarreddy12

---

## 📄 License

This project is intended for learning, development, and demonstration purposes. Add an appropriate open-source license if you plan to distribute it.