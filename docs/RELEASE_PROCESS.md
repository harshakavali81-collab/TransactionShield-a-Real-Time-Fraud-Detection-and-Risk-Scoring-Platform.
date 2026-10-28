# Reproducible source releases

## GitHub Actions archive

On pushes to `main`, CI tests Python, FastAPI, model-manifest integrity, migrations, Compose configuration, and the React build. After both Python and frontend jobs pass, the `source-bundle` job executes `git archive HEAD`, writes `TransactionShield-source.zip`, and calculates `TransactionShield-source.zip.sha256`. Both files are uploaded as one GitHub Actions artifact with 30-day retention.

Open [TransactionShield CI history](https://github.com/harshakavali81-collab/TransactionShield-a-Real-Time-Fraud-Detection-and-Risk-Scoring-Platform./actions/workflows/ci.yml), choose a successful run for the required commit, and find its source ZIP under **Artifacts**.

Check the downloaded ZIP after extracting the GitHub Actions artifact:

```bash
sha256sum -c TransactionShield-source.zip.sha256
```

The archive contains only tracked repository files. It does not include local secrets, untracked datasets, Docker images, an actual hosted endpoint, or independently authenticated real banking results.

## Source release versus production approval

These tests and the SHA-256 checksum check consistency, not cryptographic publisher identity or operational safety. A passing build is **not** an independent security assessment, real-data model certification, fraud-loss approval, or authorization to access financial transaction systems. Use the documented cloud staging Blueprint only after attaching your own hosting account and reviewing credentials, costs, monitoring, privacy and availability.

## Local verification

```bash
python scripts/verify_model_artifact.py
pytest -q
docker compose --profile streaming config --quiet
cd frontend && npm install --no-audit --no-fund && npm run build
```
