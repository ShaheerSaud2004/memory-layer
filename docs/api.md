# API & SDK

## OpenAPI

Run the API and open `http://localhost:8000/docs` for interactive OpenAPI.

Raw schema: `http://localhost:8000/openapi.json`

## Authentication

- **Users**: `Authorization: Bearer <jwt>` returned from `POST /v1/auth/register` or `POST /v1/auth/login`.
- **Agents**: `X-API-Key: aml_...` created via `POST /v1/agents` (admin/owner).

## TypeScript SDK

Package: `packages/sdk` (`MemoryLayerClient`).

Optional codegen:

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o packages/sdk/src/openapi.d.ts
```

## Highlights

- `POST /v1/memories` — ingest + chunk + embed
- `POST /v1/memories/search` — hybrid retrieval
- `GET /v1/memories/{id}/graph` — neighborhood for visualization
- `POST /v1/optimizer/run` — maintenance job (MVP summarization stub)
