#!/usr/bin/env python3
import argparse, base64, json, hashlib, sys, os, http.client, ssl, urllib.parse
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder

def sha256_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        h = hashlib.sha256()
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()
def canonical_json_bytes(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")

def load_bundle(path: str) -> dict:
    with open(path, "rb") as f: return json.load(f)
def verify_sig(bundle: dict, pubkey_hex: str):
    payload = canonical_json_bytes(bundle["payload"])
    sig_hex = bundle["sig"].split(":")[-1]
    VerifyKey(pubkey_hex, encoder=HexEncoder).verify(payload, bytes.fromhex(sig_hex))
    return payload

def http_request(base_url: str, check: dict, timeout=20) -> bytes:
    u = urllib.parse.urljoin(base_url.rstrip("/") + "/", check["path"].lstrip("/"))
    parsed = urllib.parse.urlparse(u)
    body = None
    headers = {k.lower(): v for k, v in (check.get("headers") or {}).items()}
    if "json" in check:
        body = canonical_json_bytes(check["json"])
        headers.setdefault("content-type", "application/json")
    elif "body_b64" in check:
        body = base64.b64decode(check["body_b64"])
    method = check["method"].upper()
    ctx = ssl.create_default_context()
    conn = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, context=ctx, timeout=timeout)
    try:
        path = parsed.path or "/"
        if parsed.query: path += "?" + parsed.query
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        if resp.status != int(check["expect_status"]):
            raise AssertionError(f"{check['name']}: status {resp.status} != {check['expect_status']}")
        return data
    finally:
        conn.close()

def main():
    ap = argparse.ArgumentParser(description="Verify Bauform signed bundles and optional hashes/HTTP checks.")
    ap.add_argument("bundle")
    ap.add_argument("--pubkey", required=True)
    ap.add_argument("--verify-hashes", action="store_true")
    ap.add_argument("--spec")
    ap.add_argument("--code")
    ap.add_argument("--http-checks", action="store_true")
    ap.add_argument("--links")
    args = ap.parse_args()

    bundle = load_bundle(args.bundle)
    payload_bytes = verify_sig(bundle, args.pubkey.strip())
    print("signature: OK")
    print("payload_sha256:", sha256_bytes(payload_bytes))

    hashes = (bundle["payload"].get("hashes") or {})
    if args.verify_hashes:
        if args.spec:
            spec_h = sha256_file(args.spec)
            assert spec_h == hashes.get("spec_sha256"), f"spec sha mismatch: {spec_h} != {hashes.get('spec_sha256')}"
            print("spec hash: OK")
        if args.code:
            code_h = sha256_file(args.code)
            assert code_h == hashes.get("code_sha256"), f"code sha mismatch: {code_h} != {hashes.get('code_sha256')}"
            print("code hash: OK")

    if args.http_checks:
        links_path = args.links or os.path.join(os.path.dirname(args.bundle), "links.json")
        if not os.path.exists(links_path):
            print("no links.json; skipping HTTP checks"); return
        links = json.load(open(links_path))
        base = links["live"]
        for chk in links.get("checks", []):
            data = http_request(base, chk)
            body_h = sha256_bytes(data)
            exp = chk["resp_sha256"]
            assert body_h == exp, f"{chk['name']}: resp sha mismatch {body_h} != {exp}"
            print(f"{chk['name']}: OK ({len(data)} bytes)")
if __name__ == "__main__":
    try: main()
    except Exception as e:
        print("ERROR:", e); sys.exit(1)

