#!/usr/bin/env python3
"""Extract source-bound addresses/tasks/library references. No target is contacted."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

def extract(path):
    p = Path(path)
    data = p.read_bytes()
    if len(data) > 10 * 1024 * 1024:
        raise ValueError("source exceeds 10 MiB")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("DTD/entities are not accepted")
    root = ET.fromstring(data)
    local = lambda e: e.tag.rsplit("}", 1)[-1]
    return {"filename": p.name, "sha256": hashlib.sha256(data).hexdigest(),
            "headers": [dict(e.attrib) for e in root if local(e) in ("fileHeader", "contentHeader")],
            "tasks": [dict(e.attrib) for e in root.iter() if local(e) == "task"],
            "addresses": [dict(e.attrib) for e in root.iter() if local(e) == "variable" and "address" in e.attrib],
            "libraries": [dict(e.attrib) for e in root.iter() if local(e) == "Library"],
            "scope": "XML declarations only; not installed device tree or resolved runtime ABI"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml")
    args = parser.parse_args()
    print(json.dumps(extract(args.xml), indent=2, ensure_ascii=False))
