"""Validate a locally supplied, authorized, privacy-minimized feed; NEVER post to a bank."""
import argparse
import json
from ml.data.partner_contract import read_approved_feed


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", required=True)
    p.add_argument("--labeled", action="store_true")
    p.add_argument("--data-approved", action="store_true")
    args = p.parse_args()
    if not args.data_approved:
        p.error("--data-approved is required; do not process unauthorized financial data")
    df = read_approved_feed(args.csv, labeled=args.labeled)
    print(json.dumps({"status": "schema_validated_not_identity_or_consent_verified", "rows": len(df),
                      "labeled": args.labeled, "sensitive_fields_stored": False}, indent=2))


if __name__ == "__main__":
    main()
