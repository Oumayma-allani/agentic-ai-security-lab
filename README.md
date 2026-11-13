
# Agentic AI Security Lab

A hands-on cybersecurity lab exploring API authorization,
LLM red teaming, prompt injection, and secure AI-agent tool use.

## Overview

This project simulates a multi-tenant retail promotion
management platform with an AI assistant that can retrieve
and approve promotional campaigns.

The goal is to evaluate security risks across REST APIs
and AI-powered workflows and implement practical mitigations.

## Tech Stack

- Python, FastAPI, pytest, httpx
- LangChain / LangGraph
- Groq LLM API
- GitHub Actions

## Security Scenarios

| Scenario | Observed Result |
|---|---|
| Broken Object Level Authorization | Confirmed on deliberately vulnerable endpoint |
| Cross-tenant API access | Blocked by secure endpoint |
| Direct prompt-injection attempt | Approval attempted, rejected by RBAC |
| Indirect prompt injection | Resisted in tested runs |
| Agent approval without confirmation | Blocked |
| Confirmed administrator approval | Authorized |

## Security Controls

- Token-based demo authentication
- Role-based and tenant-level authorization
- API-enforced authorization checks
- Promotion-specific human approval gate (PoC)
- Automated security regression tests

## Run Tests

```bash
python -m pytest tests/ -v
```

Current baseline: 12 passed, 1 expected failure.

The expected failure demonstrates the deliberately vulnerable
BOLA endpoint; it is not considered a secure implementation.

## Security Reports

See the `reports/` directory for recorded prompt-injection
experiments.

## Security Notice

This is an intentionally vulnerable educational project.
All records and accounts are fictional.

The vulnerable endpoint and hardcoded demo tokens must not
be used in production. Run the API locally only.

The CLI approval confirmation is a proof of concept,
not a production-grade authorization workflow.

## Roadmap

- Automated LLM red-teaming evaluations
- Authenticated OWASP ZAP API scanning
- Additional attack scenarios and mitigations
- Extended CI/CD security reporting
```
