# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of SERAMIS seriously. If you discover a security
vulnerability, please report it **privately** so we can address it before
public disclosure.

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, use one of the following channels:

- GitHub's [private vulnerability reporting](https://github.com/cartesiosson/ai_act_project/security/advisories/new)
  (preferred), or
- Email **mariano.ortegademues@gmail.com** with the subject line
  `[SECURITY] SERAMIS`.

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce (proof of concept where possible)
- The affected service/component and version

We aim to acknowledge reports within **5 business days** and to provide a
remediation timeline after triage.

## Scope and known considerations

SERAMIS is a research/academic platform. The default Docker Compose setup is
intended for **local or trusted-network deployment** and ships without
authentication and with development default credentials. Before exposing any
service to an untrusted network you should, at minimum:

- Replace all default credentials in `.env` (never use `admin`).
- Restrict CORS to known origins.
- Place the services behind an authenticating reverse proxy / TLS.
- Validate and sanitize any externally supplied input that reaches SPARQL or
  database queries.

These hardening items are tracked in the project issues.
