# Frontend Guide

The frontend is a React + TypeScript + Vite application.

It owns:

- User-facing pages
- Routing
- UI components
- API calls to the FastAPI backend
- Client-side state for server data through TanStack Query

## Current Status

Implemented now:

- React app setup
- Vite setup
- React Router setup
- TanStack Query provider
- Basic app layout
- Placeholder pages for all planned routes
- Simple home page
- API client foundation
- ESLint, Prettier, and Vitest configuration

Not implemented yet:

- Real login/register forms
- Real creator dashboard
- Real brand dashboard
- Campaign management UI
- Recommendations UI
- Proposal workflows

## Run Locally

From `frontend/`:

```bash
npm install
npm run dev
```

Open:

- `http://localhost:5173`

## Test, Lint, and Build

From `frontend/`:

```bash
npm run test
npm run lint
npm run build
```

## Folder Structure

```text
src/
|-- app/
|-- components/
|-- features/
|-- pages/
|-- services/
|-- hooks/
|-- types/
|-- utils/
|-- config/
|-- mocks/
tests/
public/
```

## `src/app/`

App-level setup.

- `App.tsx` wires global providers.
- `router.tsx` defines all frontend routes.
- `queryClient.ts` configures TanStack Query.

Beginner note: if you want to add a new page URL, update `router.tsx`.

## `src/pages/`

Route-level screens.

Examples:

- `/` uses `HomePage.tsx`
- `/login` uses `LoginPage.tsx`
- `/campaigns/:id` uses `CampaignDetailPage.tsx`

Pages should stay readable. If a page grows too large, move smaller parts into `components/` or `features/`.

## `src/components/`

Shared UI components used across multiple pages.

Current examples:

- `AppLayout.tsx`
- `PagePlaceholder.tsx`

Put a component here only if more than one feature or page can reuse it.

## `src/features/`

Feature-specific code.

Current feature folders:

- `auth/`
- `creators/`
- `brands/`
- `campaigns/`
- `proposals/`
- `recommendations/`

As features grow, each folder can contain components, hooks, types, and local helpers for that feature.

## `src/services/`

API service layer.

Use this folder for functions that call the backend.

Current file:

- `apiClient.ts`

Example future pattern:

```text
services/apiClient.ts
services/creatorsApi.ts
services/campaignsApi.ts
```

Do not call `fetch` directly from every page. Put API calls in services.

## `src/hooks/`

Reusable React hooks.

Current example:

- `useHealth.ts`

Future hooks may wrap TanStack Query for creators, campaigns, proposals, and recommendations.

## `src/types/`

Shared TypeScript types.

Use this folder for API response shapes or shared domain types.

Avoid `any`. If the backend response is known, create a clear TypeScript type.

## `src/config/`

Frontend configuration.

Current file:

- `env.ts`

Vite environment variables must start with `VITE_`.

Current variable:

- `VITE_API_BASE_URL`

## `src/mocks/`

Temporary mock data for local UI development.

Mock data helps build screens before backend endpoints are ready. Do not treat mock data as production data.

## `src/utils/`

Small reusable helper functions.

Current example:

- `formatCurrency.ts`

Keep utilities small. If a helper is only useful for one feature, place it in that feature folder instead.

## Adding A New Page

Example: adding `/settings`.

1. Create `src/pages/SettingsPage.tsx`.
2. Add the route in `src/app/router.tsx`.
3. Add a navigation link in `src/components/AppLayout.tsx` if users need it in the main nav.
4. Add feature components under `src/features/settings/` if the page grows.
5. Add a small test in `tests/`.

## Calling Backend APIs

Use the service layer.

Recommended pattern:

```text
Page -> hook -> service -> backend API
```

Example:

```text
HomePage -> useHealth -> apiGet -> GET /health
```

This keeps pages focused on UI, not networking details.
