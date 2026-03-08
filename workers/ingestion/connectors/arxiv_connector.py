from __future__ import annotations

from xml.etree import ElementTree as ET

from workers.ingestion.base import BaseConnector


class ArxivConnector(BaseConnector):
    source_name = "arxiv"

    def fetch_items(self, limit: int) -> list[dict]:
        params = {
            "search_query": 'all:("artificial intelligence" OR "machine learning" OR "llm")',
            "start": 0,
            "max_results": max(1, min(limit, 50)),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        xml_text = self._request_text("http://export.arxiv.org/api/query", params=params)
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        entries: list[dict] = []
        for entry in root.findall("atom:entry", ns):
            link = ""
            for link_node in entry.findall("atom:link", ns):
                if link_node.attrib.get("rel") == "alternate":
                    link = link_node.attrib.get("href", "")
                    break
            entries.append(
                {
                    "id": (entry.findtext("atom:id", default="", namespaces=ns) or "").strip(),
                    "title": (entry.findtext("atom:title", default="", namespaces=ns) or "").strip(),
                    "summary": (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip(),
                    "published": (entry.findtext("atom:published", default="", namespaces=ns) or "").strip(),
                    "updated": (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip(),
                    "link": link,
                }
            )
        return entries
