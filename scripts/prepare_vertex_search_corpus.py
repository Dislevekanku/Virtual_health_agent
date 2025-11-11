#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare clinical guidance corpus for Vertex AI Search.

Reads plain-text guidance from the `guidelines/` directory and produces a JSONL
file compatible with Discovery Engine import jobs. Each file is transformed into
an individual document with metadata for source attribution.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Iterable, Dict, Any
import base64


def gather_guidance_documents(source_dir: pathlib.Path) -> Iterable[Dict[str, Any]]:
    """Yield document payloads derived from guidance text files."""
    for path in sorted(source_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        document_id = path.stem.replace("_", "-").lower()
        source_name = path.stem.replace("_", " ").title()

        raw_bytes = base64.b64encode(text.encode("utf-8")).decode("utf-8")

        document = {
            "id": document_id,
            "content": {
                "mimeType": "text/plain",
                "rawBytes": raw_bytes,
            },
            "structData": {
                "title": source_name,
                "source": "Public Clinical Guidance",
                "snippet": text[:5000],  # Discovery Engine snippet limit
                "raw_text": text,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["clinical_guidance", "symptom_triage"],
                "metadata": {
                    "original_file": str(path),
                },
            },
        }
        yield document


def write_jsonl(documents: Iterable[Dict[str, Any]], output_path: pathlib.Path) -> None:
    """Write documents to a JSON Lines file."""
    with output_path.open("w", encoding="utf-8") as fh:
        for doc in documents:
            fh.write(json.dumps(doc, ensure_ascii=False))
            fh.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Vertex AI Search corpus from guidance files.")
    parser.add_argument(
        "--source-dir",
        type=pathlib.Path,
        default=pathlib.Path("guidelines"),
        help="Directory containing guidance text files (default: guidelines/).",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("artifacts/vertex_search_corpus.jsonl"),
        help="Output JSONL path for Discovery Engine import (default: artifacts/vertex_search_corpus.jsonl).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {args.source_dir}")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    documents = list(gather_guidance_documents(args.source_dir))
    if not documents:
        raise ValueError(f"No guidance documents found in {args.source_dir}")

    write_jsonl(documents, args.output)

    print(f"Wrote {len(documents)} guidance documents to {args.output}")
    print("Upload the JSONL file using `gcloud discovery-engine` or the console import workflow.")


if __name__ == "__main__":
    main()

