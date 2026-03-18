"""Tests for Microsoft Learn MCP Server models."""

import pytest
from microsoft_learn_mcp_server.models import ArticleContent, SearchResponse, SearchResult


class TestSearchResult:
    def test_basic_creation(self):
        result = SearchResult(title="Azure VM", url="https://learn.microsoft.com/en-us/azure/vm")
        assert result.title == "Azure VM"
        assert result.url == "https://learn.microsoft.com/en-us/azure/vm"
        assert result.description == ""
        assert result.category == ""
        assert result.last_updated == ""

    def test_with_all_fields(self):
        result = SearchResult(
            title="Azure Functions",
            url="https://learn.microsoft.com/en-us/azure/functions",
            description="Serverless compute service",
            category="Documentation",
            last_updated="2024-01-01T00:00:00+00:00",
        )
        assert result.description == "Serverless compute service"
        assert result.category == "Documentation"

    def test_required_fields_missing(self):
        with pytest.raises(Exception):
            SearchResult(title="Only title")

    def test_url_required(self):
        with pytest.raises(Exception):
            SearchResult(url="https://learn.microsoft.com")


class TestSearchResponse:
    def test_basic_creation(self):
        response = SearchResponse(query="azure", results=[], total=0)
        assert response.query == "azure"
        assert response.results == []
        assert response.total == 0

    def test_with_results(self):
        results = [
            SearchResult(title="Article 1", url="https://learn.microsoft.com/1"),
            SearchResult(title="Article 2", url="https://learn.microsoft.com/2"),
        ]
        response = SearchResponse(query="test", results=results, total=2)
        assert len(response.results) == 2
        assert response.results[0].title == "Article 1"

    def test_results_are_search_result_instances(self):
        result_data = [{"title": "Test", "url": "https://learn.microsoft.com"}]
        response = SearchResponse(query="test", results=result_data, total=1)
        assert isinstance(response.results[0], SearchResult)


class TestArticleContent:
    def test_basic_creation(self):
        article = ArticleContent(
            title="Azure Functions Overview",
            url="https://learn.microsoft.com/en-us/azure/functions/overview",
            content="# Overview\n\nAzure Functions is a serverless solution.",
        )
        assert article.title == "Azure Functions Overview"
        assert article.metadata == {}

    def test_with_metadata(self):
        article = ArticleContent(
            title="Article",
            url="https://learn.microsoft.com",
            content="Content",
            metadata={"ms.author": "johndoe", "ms.date": "01/01/2024"},
        )
        assert article.metadata["ms.author"] == "johndoe"

    def test_metadata_default_factory(self):
        a1 = ArticleContent(title="A1", url="https://a.com", content="c1")
        a2 = ArticleContent(title="A2", url="https://b.com", content="c2")
        a1.metadata["key"] = "value"
        assert "key" not in a2.metadata

    def test_required_fields_missing(self):
        with pytest.raises(Exception):
            ArticleContent(title="Title", url="https://learn.microsoft.com")
