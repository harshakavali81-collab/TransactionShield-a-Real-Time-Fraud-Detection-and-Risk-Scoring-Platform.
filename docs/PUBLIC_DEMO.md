# Public static preview — **offline synthetic only**

This repository includes a no-bank-data frontend preview published via GitHub Pages **if Pages is enabled** on the repository. It is deliberately **not** the fraud-scoring API or an operational risk detection service.

- `VITE_STATIC_DEMO=true` at compile time switches the React UI to `frontend/src/api/staticDemo.js`.
- Sample transactions are fictional and generated locally in the browser; scores are **rule simulation, not the trained model**.
- The Model Performance page shows checked-in **synthetic** training evaluation, distinct from the offline simulation.
- Clicking Score modifies only in-memory browser sample data; a refresh resets the preview.
- No real transactions, model, database, provider endpoints or banking credentials are used or exposed.

## Deploy

1. Repository Settings → Pages → Source → **GitHub Actions**.
2. Open **Actions → Publish offline synthetic UI preview** and run it (or push updated frontend files).
3. If successful, open the `github-pages` environment URL shown by Actions. GitHub Pages availability and GitHub permissions are controlled by GitHub, not this project.
4. This deployment is **frontend only**; it cannot prove production backend hosting, fraud effectiveness or security certification.

The Pages workflow uses a repository-specific Vite `base` path. If you rename the repository, change `GITHUB_PAGES_BASE` accordingly.

For an authenticated API with managed Postgres and TLS, see [Cloud staging](CLOUD_STAGING.md). Never expose the backend as a public payments decision engine solely because Pages deployment succeeds.
