"""Retrieve reproducible Phase 2 codebook and OECD policy-source snapshots."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    "ches_codebook": (
        "https://github.com/chesdata/chesdata.github.io/releases/download/ches-trend/1999-2024_CHES_codebook.pdf",
        ROOT / "data" / "raw" / "documentation" / "1999-2024_CHES_codebook.pdf",
    ),
    "parlgov_codebook": (
        "https://www.parlgov.org/data/codebook.pdf",
        ROOT / "data" / "raw" / "documentation" / "parlgov_codebook_2023.pdf",
    ),
    "oecd_pf32": (
        "https://webfs.oecd.org/Els-com/Family_Database/PF3_2_Enrolment_childcare_preschool.xlsx",
        ROOT / "data" / "raw" / "oecd" / "PF3_2_Enrolment_childcare_preschool.xlsx",
    ),
}


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "FairWork-source-audit/0.1"})
    with urlopen(request, timeout=120) as response:  # nosec B310: fixed public source URLs
        return response.read()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Download again even if the local snapshot exists.")
    args = parser.parse_args()
    for source_id, (url, path) in SOURCES.items():
        if path.exists() and not args.refresh:
            body = path.read_bytes()
            state = "reused"
        else:
            body = fetch(url)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            state = "downloaded"
        print(f"{source_id}: {state}, sha256={hashlib.sha256(body).hexdigest()}")


if __name__ == "__main__":
    main()
