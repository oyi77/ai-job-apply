# Pages Directory AGENTS.md

**OVERVIEW**: Route-based page components with lazy loading.

## STRUCTURE
- **Core**: Dashboard, Applications, Resumes, JobSearch
- **AI Tools**: AIServices (optimization, interview prep)
- **Insights**: Analytics (charts), CoverLetters, Settings
- **Auth**: Login, Register, PasswordReset

## WHERE TO LOOK
| Page | Features |
|------|----------|
| `Dashboard.tsx` | Quick actions, intelligence overview |
| `Applications.tsx` | Bulk actions, export modal |
| `JobSearch.tsx` | Multi-platform search, filtering |
| `AIServices.tsx` | Resume optimization, interview prep |
| `Analytics.tsx` | Charts, success rates |

## CONVENTIONS
- **Lazy Loading**: Use `React.lazy()` in `App.tsx` for all page components.
- **Data Fetching**: React Query mandatory for server state (`useQuery`, `useMutation`).
- **State Management**: Zustand (`appStore.ts`) for global UI/App state.
- **Security**: Protected routes via `<ProtectedRoute>` wrapper.

## ANTI-PATTERNS
- **No Local Server State**: Do not store server data in `useState`; use React Query.
- **No Direct API Calls**: Use `services/api.ts` layer (e.g., `applicationService`).

## NOTES
- Data layer uses `applicationService`, `jobSearchService`, `aiService`.
- Keep components lean; move complex logic to hooks or services.
