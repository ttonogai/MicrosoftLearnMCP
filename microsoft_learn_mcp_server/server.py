"""Microsoft Learn MCP Server."""

from fastmcp import FastMCP
from .client import MicrosoftLearnClient

mcp = FastMCP(
    "microsoft-learn-mcp-server",
    instructions=(
        "This server provides tools to search and read Microsoft Learn "
        "technical documentation articles."
    ),
)

_client = MicrosoftLearnClient()


@mcp.tool(
    name="search_documentation",
    description=(
        "Search Microsoft Learn technical documentation for articles matching the query. "
        "Returns a list of relevant articles with titles, URLs, and descriptions."
    ),
)
async def search_documentation(query: str, locale: str = "en-us") -> str:
    """Search Microsoft Learn documentation.

    Args:
        query: Search query string.
        locale: Language/locale for results (default: 'en-us', e.g. 'ja-jp').

    Returns:
        Formatted string containing search results.
    """
    import json
    results = await _client.search(query=query, locale=locale)
    return json.dumps({"query": query, "locale": locale, "results": results}, ensure_ascii=False, indent=2)


@mcp.tool(
    name="read_documentation",
    description=(
        "Retrieve the full content of a Microsoft Learn article at the given URL. "
        "Returns the article title, body text in Markdown format, and metadata."
    ),
)
async def read_documentation(url: str) -> dict:
    """Fetch article content from a Microsoft Learn URL.

    Args:
        url: URL of the Microsoft Learn article to retrieve.

    Returns:
        dict containing article title, content (Markdown), and metadata.
    """
    return await _client.read_article(url=url)


def main() -> None:
    """Entry point for the Microsoft Learn MCP Server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
