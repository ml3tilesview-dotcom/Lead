# MANUAL_ACTIONS.md

Actions that require the repository owner and cannot be completed automatically by Claude Code.

---

## Required Before First Run

| # | Action | Detail |
|---|--------|--------|
| 1 | Copy `.env.example` to `.env` | `cp .env.example .env` and fill in values |
| 2 | Install Docker Desktop | https://www.docker.com/products/docker-desktop/ |

---

## Phase 1 — No External Accounts Required

Phase 1 uses only Docker, PostgreSQL (local), and a deterministic rule-based classifier.
No external API keys are needed to run Phase 1.

---

## Future Phases — External Accounts Required

| # | Account / Credential | Purpose | Phase |
|---|----------------------|---------|-------|
| 1 | OpenAI API key (`OPENAI_API_KEY`) | AI-powered lead classification and reply generation | Phase 2 |
| 2 | Meta Developer Account | Facebook Messenger and Instagram DM/Comment integration | Phase 3 |
| 3 | Facebook Page (connected to Meta App) | Receive Messenger messages | Phase 3 |
| 4 | Instagram Professional Account | Instagram DMs and comment replies | Phase 3 |
| 5 | Meta App — Permissions | `pages_messaging`, `instagram_basic`, `instagram_manage_messages` | Phase 3 |
| 6 | Meta App — Webhook Verification | Set verify token and endpoint URL in Meta dashboard | Phase 3 |
| 7 | LinkedIn Developer Application | LinkedIn message integration | Phase 4 |
| 8 | LinkedIn API Approval | `w_member_social`, `r_emailaddress` | Phase 4 |
| 9 | n8n Instance | Handoff webhook automation | Phase 2 |
| 10 | n8n Webhook URL (`N8N_HANDOFF_WEBHOOK_URL`) | Notify sales team on hot-lead handoff | Phase 2 |
| 11 | Verified TilesView/TilesWale product information | Accurate product descriptions, pricing tiers, supported integrations | Before production |
| 12 | Production hosting (Railway / Render / AWS / GCP) | Deploy the backend and database | Phase 5 |
| 13 | Custom domain and SSL certificate | Production URL | Phase 5 |

---

## Git Push

GitHub authentication must be configured before pushing.

```bash
git status
git add .
git commit -m "Complete phase 1 lead generation backend"
git push -u origin main
```

If using HTTPS and prompted for credentials, use a GitHub Personal Access Token (PAT)
as the password. Create one at: https://github.com/settings/tokens
