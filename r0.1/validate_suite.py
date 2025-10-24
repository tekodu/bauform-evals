#!/usr/bin/env python3
import json, os, sys
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder

def canon_bytes(obj):
    import json as _j; return _j.dumps(obj, separators=(",", ":"), sort_keys=True).encode()

def main(idx_path, pubkey_path):
    pub = open(pubkey_path, "r").read().strip()
    idx = json.load(open(idx_path, "rb"))
    payload = canon_bytes(idx["payload"])
    sig_hex = idx["sig"].split(":")[-1]
    VerifyKey(pub, encoder=HexEncoder).verify(payload, bytes.fromhex(sig_hex))
    print("suite signature: OK")
    suite_dir = os.path.dirname(idx_path)
    spec_dirs = sorted(d for d in os.listdir(suite_dir) if os.path.isdir(os.path.join(suite_dir, d)) and d.endswith("_v1"))
    index_specs = sorted(s["spec_id"] for s in idx["payload"]["specs"])
    assert index_specs == spec_dirs, f"coverage mismatch: index={index_specs} dirs={spec_dirs}"
    for s in idx["payload"]["specs"]:
        p = os.path.join(suite_dir, s["path"])
        assert os.path.exists(p), f"missing bundle {p}"
    print("suite coverage: OK")
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: validate_suite.py r0.1/suite.index.json.signed r0.1/public_key.txt"); sys.exit(2)
    main(sys.argv[1], sys.argv[2])

