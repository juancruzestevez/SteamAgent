import pytest
from unittest.mock import patch, MagicMock
from src.tools.rag import query_wiki_tool

@patch("src.tools.rag.WebBaseLoader")
@patch("src.tools.rag.BM25Retriever")
def test_query_wiki_tool_success(mock_retriever, mock_loader):
    from langchain_core.documents import Document
    # Real Document
    doc = Document(page_content="Para vencer a Margit usa el grillete.", metadata={"source": "fake"})
    
    mock_loader_instance = MagicMock()
    mock_loader_instance.load.return_value = [doc]
    mock_loader.return_value = mock_loader_instance

    # Mock BM25
    mock_retriever_instance = MagicMock()
    mock_retriever_instance.invoke.return_value = [doc]
    mock_retriever.from_documents.return_value = mock_retriever_instance

    result = query_wiki_tool("https://fake.wiki|como vencer a margit")
    
    assert "Contexto extraído" in result
    assert "grillete" in result

def test_query_wiki_tool_invalid_format():
    result = query_wiki_tool("solo una URL sin pregunta")
    assert "Error de formato" in result
