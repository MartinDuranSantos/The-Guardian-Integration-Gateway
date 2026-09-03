# 🔒 Secure Inquiry API

A production-ready FastAPI service that securely processes user inquiries by sanitizing PII, guarding downstream AI services with a circuit breaker, and maintaining encrypted audit trails.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🔐 PII Sanitization** | Automatically redacts emails, credit cards, and SSNs from incoming messages |
| **🤖 Mock AI Integration** | Simulates an external AI provider with realistic 2-second latency |
| **⚡ Circuit Breaker** | Fails fast after 3 consecutive AI failures — no timeout penalty |
| **📝 Encrypted Audit Logs** | Stores original messages encrypted (Fernet) and sanitized messages in plaintext |
| **🧪 Full Test Suite** | Self-contained tests with zero external dependencies |


### Request Lifecycle

1. **Sanitization** — Strips emails, credit cards (13–19 digits), and SSNs (`###-##-####` or 9 digits)
2. **Circuit Breaker Guard** — Tracks AI health; opens after 3 failures for instant fallback
3. **Mock AI Call** — Simulated 2-second downstream call returning `"Generated Answer."`
4. **Audit Logging** — Persists encrypted original + plaintext sanitized message to `audit_db.json`

---

## 📁 Project Structure

```
secure-inquiry-api/
├── main.py              # FastAPI application entry point
├── routes
  ├── routes.py            # API endpoints (/secure-inquiry, /health)
├── schemas
  ├── schemas.py           # Pydantic request/response models
├── services
  ├── ai_service.py        # Mock external AI provider
  ├── audit_service.py     # Encrypted JSON-file audit database
├── use_cases
  ├── 01_simplerequest.py
  ├── 02_AI_service_bussy.py
├── utils
  ├── sanitizer.py         # PII detection and redaction engine
  ├── circuit_breaker.py   # Async circuit breaker implementation
└── README.md            # This file
```



## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- `pip`

### Installation

```bash
# Clone the repository
git clone https://github.com/MartinDuranSantos/The-Guardian-Integration-Gateway.git
cd The_Guardian_Integration_Gateway

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the server
cd app
fastapi dev
```

The API will be available at `http://localhost:8000`.

---

## 📡 API Reference

### `POST /secure-inquiry`

Processes a user inquiry through the full pipeline.

#### Request Body

```json
{
  "userId": "usr_42",
  "message": "Contact me at %Email%. My SSN is %SSN%."
}
```

#### Response Body

```json
{
  "userId": "usr_42",
  "original_message": "Contact me at %Email%. My SSN is %SSN%.",
  "sanitized_message": "Contact me at <REDACTED: EMAIL>. My SSN is <REDACTED: SSN>.",
  "redactions_found": ["SSN", "EMAIL"],
  "generated_answer": "Generated Answer.",
  "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

#### Circuit Breaker Fallback Response

When the AI service has failed 3 times consecutively:

```json
{
  "userId": "usr_42",
  "original_message": "...",
  "sanitized_message": "...",
  "redactions_found": [...],
  "generated_answer": "Service Busy",
  "audit_id": "..."
}
```

> **Note:** The fallback returns **instantly** — no 2-second timeout wait.

### `GET /health`

Health check endpoint.

```json
{
  "status": "ok"
}
```


### Test Coverage

| Test | Scenario |
|------|----------|
| **Test 1** | Normal operation — AI responds successfully |
| **Test 2** | 3 consecutive AI failures open the circuit |
| **Test 3** | 4th request while OPEN returns `"Service Busy"` instantly (< 0.5s) |
| **Test 4** | Circuit recovers to CLOSED after 30s timeout + successful retry |

---

## 🔌 Example Clients

### cURL

```bash
curl -X POST http://localhost:8000/secure-inquiry \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "usr_42",
    "message": "My email is %Email% and card is %CardNumber%."
  }'
```

### Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/secure-inquiry",
    json={
        "userId": "usr_42",
        "message": "My SSN is %SSN%. Help me please."
    }
)
print(response.json())
```

---

## 🔐 Security Notes

- **Original messages** are encrypted at rest using Fernet symmetric encryption
- **Sanitized messages** are stored in plaintext for compliance review
- The demo encryption key is auto-generated at runtime — **in production**, load from a secure key management service (AWS KMS, HashiCorp Vault, etc.)
- Credit card detection uses 13–19 digit matching without storing or validating prefixes

---

## ⚙️ Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `failure_threshold` | `3` | Consecutive AI failures before circuit opens |
| `recovery_timeout` | `30s` | Seconds before circuit enters half-open state |
| `AI latency` | `2s` | Simulated downstream network delay |
| `audit_db.json` | auto-created | Local JSON audit trail |

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 🙋 Questions?

Open an issue or reach out via GitHub Discussions.
