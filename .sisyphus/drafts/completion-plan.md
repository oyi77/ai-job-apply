# Draft: Codebase Completion & UI/UX Overhaul

## Requirements (confirmed)
- [requirement]: Plan the completion of the codebase based on its goals.
- [requirement]: Improve the UI/UX design.
- [requirement]: **Notifications**: Implement both Email and Web Push notifications.
- [requirement]: **Mobile**: specific PWA implementation (manifest, service workers, offline support).
- [requirement]: **UI/UX**: Address "generic" look and "non-descriptive" content. Focus on branding, clearer copywriting, and visual storytelling.
- [requirement]: **AI/Analytics**: Connect frontend to backend. Upgrade "Skills Gap" to use Gemini (AI) and statistical trends (ML).

## Current State Analysis (Audit Results)
- **Authentication**: ✅ **Fully Implemented**. Backend (JWT, Refresh, Rate Limiting) and Frontend (Login/Register/Protected Routes) are working. README is outdated regarding this.
- **Analytics**: ⚠️ **Partially Implemented**.
    - Backend: Endpoints exist but `get_skills_gap_analysis` uses hardcoded keywords, not AI.
    - Frontend: Displays **mock data**. Not connected to advanced backend endpoints.
- **UI/UX**: Functional React/Tailwind setup. "Mobile-first" approach mentioned but user feels it's generic.

## Technical Decisions
- [decision]: **Auth** is considered complete (skip re-implementation).
- [decision]: **Analytics** needs: 1) Frontend integration, 2) Backend AI upgrade (Gemini), 3) ML/Stats integration.
- [decision]: **Mobile Strategy**: PWA (Progressive Web App) instead of native.
- [decision]: **Notifications**: Hybrid approach (Email for critical updates, Push for real-time alerts).

## Research Findings
- [source]: `backend/src/api/v1/auth.py` & `frontend/src/pages/Login.tsx` confirm Auth is done.
- [source]: `frontend/src/pages/Analytics.tsx` contains hardcoded mock data.
- [source]: `package.json` shows `vitest` and `@testing-library`. Backend has `tests/` folder. Test infra exists.

## Open Questions
- [question]: Email Provider? (Will default to SMTP/Console for dev, suggest SendGrid/AWS for prod in plan).

## Scope Boundaries
- INCLUDE: Connecting Analytics Frontend to Backend.
- INCLUDE: Upgrading Analytics logic to AI (Gemini).
- INCLUDE: Notification System (Email + Web Push).
- INCLUDE: UI/UX Redesign (Theme, Typography, Copywriting).
- INCLUDE: PWA Configuration.
- EXCLUDE: Re-implementing Auth (already done).
- EXCLUDE: Native Mobile Apps (React Native/Flutter).
