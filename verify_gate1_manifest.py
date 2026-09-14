#!/usr/bin/env python3
"""Check SHA-256 byte identity for the Gate-1 package; no validity claims."""

import hashlib
import json
from pathlib import Path
import sys


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "gate1_manifest.json").read_text(encoding="utf-8"))
    errors = []
    entries = manifest["files"]
    for name, expected in entries.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"Invalid manifest path: {name}")
            continue
        path = root / relative
        if not path.is_file():
            errors.append(f"Missing: {name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"SHA-256 mismatch: {name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Verified {len(entries)} Gate-1/source file hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
