"""Formatters for Microsoft Learn MCP Server."""

from .models import ArticleContent, SearchResponse


def format_search_results(response: SearchResponse) -> str:
    """検索結果をMarkdown形式にフォーマット"""
    lines = [
        f"# Search Results for: {response.query}",
        "",
        f"Found {response.total} result(s)",
        "",
    ]
    for i, result in enumerate(response.results, 1):
        lines.append(f"## {i}. {result.title}")
        lines.append("")
        lines.append(f"**URL:** {result.url}")
        if result.category:
            lines.append(f"**Category:** {result.category}")
        if result.last_updated:
            lines.append(f"**Last Updated:** {result.last_updated}")
        if result.description:
            lines.append("")
            lines.append(result.description)
        lines.append("")
    return "\n".join(lines)


def format_article(article: ArticleContent) -> str:
    """記事内容をMarkdown形式にフォーマット"""
    lines = [
        f"# {article.title}",
        "",
        f"**URL:** {article.url}",
    ]
    if article.metadata:
        lines += ["", "## Metadata", ""]
        for key, value in article.metadata.items():
            lines.append(f"- **{key}:** {value}")
    lines += ["", "## Content", "", article.content]
    return "\n".join(lines)
