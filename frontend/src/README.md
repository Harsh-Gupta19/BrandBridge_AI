# Frontend Source Guide

This folder contains the React application source code.

## Mental Model

The frontend should follow this flow:

```text
Route page
  -> feature or shared component
  -> hook
  -> service/API client
  -> FastAPI backend
```

## Folder Responsibilities

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
```

## `app/`

Application-level setup.

- `App.tsx` renders global providers.
- `router.tsx` defines page routes.
- `queryClient.ts` configures TanStack Query.

Change `router.tsx` when adding a new URL.

## `pages/`

One component per route.

Examples:

- `HomePage.tsx`
- `LoginPage.tsx`
- `CampaignsPage.tsx`
- `CreatorProfilePage.tsx`

Pages should describe the screen. Move reusable UI into `components/` or `features/`.

## `components/`

Reusable UI shared across multiple pages or features.

Examples:

- App layout
- Page placeholder
- Future buttons, tables, modals, and shared form controls

## `features/`

Feature-specific code.

Examples:

- `features/auth/`
- `features/creators/`
- `features/campaigns/`
- `features/recommendations/`

If code is only useful for one feature, keep it inside that feature folder.

## `services/`

Backend API calls.

Do not spread raw `fetch` calls across many pages. Put API calls here.

## `hooks/`

Reusable React hooks.

Use hooks to connect React pages/components to services or shared state.

## `types/`

Shared TypeScript types.

Avoid `any`. Prefer explicit types that match backend schemas.

## `utils/`

Small helper functions.

If a helper becomes feature-specific, move it into the matching feature folder.

## `config/`

Frontend configuration, especially Vite environment variables.

Vite exposes only variables starting with `VITE_`.

## `mocks/`

Temporary mock data for UI development.

Do not treat mock data as production data.
