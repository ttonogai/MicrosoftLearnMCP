"""Microsoft Learn MCP Server - HTTP Client"""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

TIMEOUT = 30.0
LEARN_SEARCH_URL = "https://learn.microsoft.com/api/search"

_GITHUB_BLOB_RE = re.compile(
    r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.*)"
)


def _github_blob_to_raw(github_url: str) -> str | None:
    """GitHub blob URL を raw.githubusercontent.com URL に変換する。"""
    m = _GITHUB_BLOB_RE.match(github_url)
    if not m:
        return None
    owner, repo, branch, path = m.groups()
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"


class MicrosoftLearnClient:
    BASE_URL = "https://learn.microsoft.com"

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            headers=HEADERS,
            timeout=TIMEOUT,
            follow_redirects=True,
        )

    async def __aenter__(self) -> "MicrosoftLearnClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.aclose()

    async def search(
        self,
        query: str,
        locale: str = "en-us",
        max_results: int = 10,
    ) -> list[dict]:
        """Microsoft Learn Search APIでドキュメントを検索する。"""
        params = {
            "search": query,
            "locale": locale,
            "$top": max_results,
            "$skip": 0,
        }
        try:
            resp = await self._client.get(LEARN_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.error("Search request failed: %s", exc)
            return []
        except Exception as exc:
            logger.error("Search parse error: %s", exc)
            return []
        return self._parse_search_response(data)

    def _parse_search_response(self, data: dict) -> list[dict]:
        results: list[dict] = []
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "category": item.get("category", ""),
                "last_updated": item.get("lastUpdatedDate", ""),
            })
        return results

    async def read_article(self, url: str) -> dict:
        """指定URLのドキュメント記事を取得する。

        GitHub の raw Markdown を優先して取得し、
        取得できない場合は HTML パースにフォールバックする。
        """
        try:
            response = await self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error("Article fetch failed: %s", exc)
            return {"title": "", "content": "", "url": url, "metadata": {}, "error": f"HTTP {exc.response.status_code}"}
        except httpx.RequestError as exc:
            logger.error("Article fetch error: %s", exc)
            return {"title": "", "content": "", "url": url, "metadata": {}, "error": str(exc)}

        soup = BeautifulSoup(response.text, "html.parser")
        title = self._extract_title(soup)
        metadata = self._extract_metadata(soup)

        content = await self._fetch_github_markdown(soup)
        if not content:
            logger.debug("Falling back to HTML parse")
            content = self._extract_content(soup)

        return {"title": title, "content": content, "url": url, "metadata": metadata}

    async def _fetch_github_markdown(self, soup: BeautifulSoup) -> str:
        """HTML 内の edit リンクから GitHub raw Markdown を取得する。"""
        edit_link = soup.find("a", attrs={"data-bi-name": "edit"})
        if not edit_link:
            return ""
        github_url = edit_link.get("href", "")
        raw_url = _github_blob_to_raw(github_url)
        if not raw_url:
            return ""
        try:
            resp = await self._client.get(raw_url)
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPError as exc:
            logger.warning("GitHub raw fetch failed: %s", exc)
            return ""

    def _extract_title(self, soup: BeautifulSoup) -> str:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """フォールバック用 HTML パース。"""
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        for selector in ["main[data-bi-name='content']", "main", "article", "div[role='main']"]:
            content_el = soup.select_one(selector)
            if content_el:
                return self._html_to_markdown(content_el)
        return soup.get_text(separator="\n", strip=True)

    def _html_to_markdown(self, element: Any) -> str:
        lines: list[str] = []
        for tag in element.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "code", "hr"],
            recursive=True,
        ):
            text = tag.get_text(separator=" ", strip=True)
            if not text:
                continue
            name = tag.name
            if name == "h1":
                lines.append(f"# {text}\n")
            elif name == "h2":
                lines.append(f"## {text}\n")
            elif name == "h3":
                lines.append(f"### {text}\n")
            elif name == "h4":
                lines.append(f"#### {text}\n")
            elif name in ("h5", "h6"):
                lines.append(f"##### {text}\n")
            elif name == "p":
                lines.append(f"{text}\n")
            elif name == "li":
                lines.append(f"- {text}")
            elif name in ("pre", "code"):
                lines.append(f"```\n{text}\n```\n")
            elif name == "hr":
                lines.append("---\n")
        if not lines:
            return element.get_text(separator="\n", strip=True)
        return "\n".join(lines)

    def _extract_metadata(self, soup: BeautifulSoup) -> dict:
        metadata: dict[str, str] = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property") or ""
            content = meta.get("content") or ""
            if name and content:
                metadata[name] = content
        return metadata
