# Bauform Evals — Signed Artifacts (r0.1)

Results-only verification bundles. No prompts or engine code.

## Verify a single bundle
```bash
pip install pynacl
python r0.1/verify_bundle.py r0.1/<spec_id>/result.json.signed --pubkey $(tr -d '\n\r' < r0.1/public_key.txt)
```

## Verify all bundles
```bash
for b in r0.1/*/result.json.signed; do
  echo "Checking $b"
  python r0.1/verify_bundle.py "$b" --pubkey $(tr -d '\n\r' < r0.1/public_key.txt) || exit 1
done
```

## Suite coverage + signature
```bash
python r0.1/validate_suite.py r0.1/suite.index.json.signed r0.1/public_key.txt
```

## Schema
Canonical JSON (compact, sorted) signed with Ed25519 over `payload`, stored as:
```json
{"payload":{...},"sig":"ed25519:<hex>"}
```

