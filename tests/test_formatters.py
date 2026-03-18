"""Tests for Microsoft Learn MCP Server formatters."""

from microsoft_learn_mcp_server.formatters import format_article, format_search_results
from microsoft_learn_mcp_server.models import ArticleContent, SearchResponse, SearchResult


class TestFormatSearchResults:
    def test_empty_results(self):
        response = SearchResponse(query="nothing", results=[], total=0)
        output = format_search_results(response)
        assert "nothing" in output
        assert "0 result(s)" in output

    def test_single_result(self):
        results = [
            SearchResult(
                title="Azure Virtual Machines",
                url="https://learn.microsoft.com/en-us/azure/virtual-machines/",
                description="Learn about Azure VMs.",
                category="Documentation",
                last_updated="2024-01-01T00:00:00+00:00",
            )
        ]
        response = SearchResponse(query="azure vm", results=results, total=1)
        output = format_search_results(response)
        assert "azure vm" in output
        assert "Azure Virtual Machines" in output
        assert "https://learn.microsoft.com/en-us/azure/virtual-machines/" in output
        assert "Learn about Azure VMs." in output
        assert "Documentation" in output
        assert "1 result(s)" in output

    def test_multiple_results(self):
        results = [
            SearchResult(title=f"Article {i}", url=f"https://learn.microsoft.com/{i}")
            for i in range(3)
        ]
        response = SearchResponse(query="test", results=results, total=3)
        output = format_search_results(response)
        assert "3 result(s)" in output
        assert "Article 0" in output
        assert "Article 2" in output

    def test_output_is_markdown(self):
        response = SearchResponse(query="test", results=[], total=0)
        output = format_search_results(response)
        assert output.startswith("#")

    def test_numbered_results(self):
        results = [
            SearchResult(title="First", url="https://learn.microsoft.com/1"),
            SearchResult(title="Second", url="https://learn.microsoft.com/2"),
        ]
        response = SearchResponse(query="test", results=results, total=2)
        output = format_search_results(response)
        assert "1." in output
        assert "2." in output

    def test_result_without_optional_fields(self):
        results = [SearchResult(title="Minimal", url="https://learn.microsoft.com")]
        response = SearchResponse(query="test", results=results, total=1)
        output = format_search_results(response)
        assert "Minimal" in output


class TestFormatArticle:
    def test_basic_article(self):
        article = ArticleContent(
            title="How to use Azure Functions",
            url="https://learn.microsoft.com/en-us/azure/functions",
            content="## Getting Started\n\nCreate your first function.",
        )
        output = format_article(article)
        assert "How to use Azure Functions" in output
        assert "https://learn.microsoft.com/en-us/azure/functions" in output
        assert "Getting Started" in output

    def test_article_with_metadata(self):
        article = ArticleContent(
            title="Test Article",
            url="https://learn.microsoft.com",
            content="Content here",
            metadata={"ms.author": "support", "ms.date": "01/01/2024"},
        )
        output = format_article(article)
        assert "ms.author" in output
        assert "support" in output

    def test_article_without_metadata(self):
        article = ArticleContent(
            title="Simple Article",
            url="https://learn.microsoft.com",
            content="Simple content",
        )
        output = format_article(article)
        assert "Simple Article" in output
        assert "Metadata" not in output

    def test_output_starts_with_title(self):
        article = ArticleContent(
            title="Test", url="https://learn.microsoft.com", content="Content"
        )
        output = format_article(article)
        assert output.startswith("# Test")

    def test_content_section_present(self):
        article = ArticleContent(
            title="Test", url="https://learn.microsoft.com", content="Article body text"
        )
        output = format_article(article)
        assert "## Content" in output
        assert "Article body text" in output
