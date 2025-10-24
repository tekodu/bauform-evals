#!/usr/bin/env python3
"""
Sign all result.json files in r1.0 suite.

Usage:
    python sign_all.py --privkey /path/to/private_key.txt

Requires: pynacl
"""

import argparse
import json
import pathlib
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder


def sign_file(path: pathlib.Path, signing_key: SigningKey):
    """Sign a single result.json file."""
    unsigned = json.load(path.open())
    
    # Canonical payload
    payload_bytes = json.dumps(
        unsigned,
        separators=(",", ":"),
        sort_keys=True
    ).encode("utf-8")
    
    # Sign
    signature = signing_key.sign(payload_bytes).signature
    sig_hex = signature.hex()
    
    # Create signed bundle
    signed = {
        "payload": unsigned,
        "sig": f"ed25519:{sig_hex}"
    }
    
    # Write signed file
    signed_path = path.parent / "result.json.signed"
    signed_path.write_text(
        json.dumps(signed, indent=2, separators=(",", ": "), sort_keys=True)
    )
    
    print(f"✅ Signed: {signed_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--privkey", required=True, help="Path to Ed25519 private key (hex)")
    args = parser.parse_args()
    
    # Load signing key
    with open(args.privkey) as f:
        privkey_hex = f.read().strip()
    
    signing_key = SigningKey(privkey_hex, encoder=HexEncoder)
    
    # Sign all result.json files
    suite_dir = pathlib.Path(__file__).parent
    result_files = list(suite_dir.glob("*/result.json"))
    
    if not result_files:
        print("⚠️  No result.json files found to sign.")
        return
    
    for result_json in result_files:
        sign_file(result_json, signing_key)
    
    print(f"\n✅ All {len(result_files)} files signed. Ready for public release.")


if __name__ == "__main__":
    main()

