#!/usr/bin/env python3
"""Search arXiv for the latest papers on a given topic.

Usage:
    python scripts/search_arxiv.py --topic "large language model"
    python scripts/search_arxiv.py --topic "diffusion model" --max-results 15

Outputs JSON to stdout with paper title, authors, summary, categories, and link.
"""

import argparse
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# Force UTF-8 output on all platforms (especially Windows with GBK)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ARXIV_API_URL = "https://export.arxiv.org/api/query"

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "https://arxiv.org/schemas/atom",
}


_ARXIV_ID_RE = re.compile(r"arxiv\.org/abs/([^/v]+)")


def extract_arxiv_id(link: str) -> str | None:
    """Extract arXiv ID from the abstract page URL, stripping version suffix."""
    m = _ARXIV_ID_RE.search(link)
    return m.group(1) if m else None


def build_query(topic: str, max_results: int) -> str:
    """Build arXiv API query URL sorted by submission date (newest first)."""
    words = topic.strip().split()
    query_parts = [f"all:{w}" for w in words] if words else [f"all:{topic}"]
    search_query = "+AND+".join(query_parts)
    query_string = (
        f"search_query={search_query}"
        f"&start=0&max_results={max_results}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )
    return f"{ARXIV_API_URL}?{query_string}"


def fetch_xml(url: str) -> bytes:
    """Fetch XML from arXiv API."""
    req = urllib.request.Request(url, headers={"User-Agent": "ArxivDetectSkill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_papers(xml_data: bytes) -> list[dict]:
    """Parse Atom XML into a list of paper dicts."""
    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall("atom:entry", NS):
        title_el = entry.find("atom:title", NS)
        summary_el = entry.find("atom:summary", NS)
        published_el = entry.find("atom:published", NS)
        updated_el = entry.find("atom:updated", NS)
        link_el = entry.find("atom:id", NS)
        comment_el = entry.find("arxiv:comment", NS)

        paper = {
            "title": _clean(title_el),
            "summary": _clean(summary_el),
            "published": published_el.text if published_el is not None else "",
            "updated": updated_el.text if updated_el is not None else "",
            "link": link_el.text if link_el is not None else "",
            "authors": [],
            "categories": [],
        }

        if comment_el is not None and comment_el.text:
            paper["comment"] = _clean(comment_el)

        for author in entry.findall("atom:author", NS):
            name_el = author.find("atom:name", NS)
            if name_el is not None and name_el.text:
                paper["authors"].append(name_el.text.strip())

        for cat in entry.findall("atom:category", NS):
            term = cat.get("term")
            if term:
                paper["categories"].append(term)

        paper["arxiv_id"] = extract_arxiv_id(paper["link"])

        papers.append(paper)

    return papers


def _clean(el) -> str:
    """Collapse whitespace in an element's text."""
    if el is None or el.text is None:
        return ""
    return " ".join(el.text.split())


def download_pdf(arxiv_id: str, output_dir: str) -> str | None:
    """Download PDF from arXiv, return local path or None on failure."""
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    os.makedirs(output_dir, exist_ok=True)
    local_path = os.path.join(output_dir, f"{arxiv_id}.pdf")
    if os.path.exists(local_path):
        return local_path
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "ArxivDetectSkill/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(local_path, "wb") as f:
            f.write(data)
        return local_path
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Search arXiv for the latest papers")
    parser.add_argument(
        "--topic", required=True, help="Search topic (e.g. 'large language model')"
    )
    parser.add_argument(
        "--max-results", type=int, default=10, help="Max results (default: 10)"
    )
    parser.add_argument(
        "--download", action="store_true",
        help="Download PDFs to the output directory"
    )
    parser.add_argument(
        "--output-dir", default="./arxiv_papers",
        help="Directory to save downloaded PDFs (default: ./arxiv_papers)"
    )
    args = parser.parse_args()

    try:
        url = build_query(args.topic, args.max_results)
        xml_data = fetch_xml(url)
        papers = parse_papers(xml_data)

        if args.download:
            for paper in papers:
                arxiv_id = paper.get("arxiv_id")
                if arxiv_id:
                    paper["download_path"] = download_pdf(arxiv_id, args.output_dir)
                else:
                    paper["download_path"] = None
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps(papers, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
