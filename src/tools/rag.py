import logging
from langchain_core.tools import Tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever

logger = logging.getLogger(__name__)


def query_wiki_tool(query_string: str) -> str:
    """Extrae información específica de una página web larga (como una wiki)."""
    try:
        # El input del agente debe ser URL|Pregunta
        parts = query_string.split("|", 1)
        if len(parts) != 2:
            return "Error de formato. Usa exactamente este formato: URL|pregunta (ejemplo: https://wiki.com/page|como vencer al jefe)"
        
        url = parts[0].strip()
        question = parts[1].strip()
        
        logger.debug("Iniciando RAG (BM25) on-the-fly para URL: %s, Pregunta: %s", url, question)
        
        # 1. Cargar la página web
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        if not docs:
            return f"No se pudo extraer texto de la URL: {url}"
            
        # 2. Dividir el texto en fragmentos (Chunks)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # 3. Buscar usando BM25 (sin necesidad de embeddings pesados)
        retriever = BM25Retriever.from_documents(splits)
        retriever.k = 3
        
        relevant_docs = retriever.invoke(question)
        
        if not relevant_docs:
            return "No se encontró información relevante en esa página para tu pregunta."
            
        # 4. Formatear la respuesta
        context = "\n\n---\n\n".join([doc.page_content.replace('\n', ' ').strip() for doc in relevant_docs])
        return f"Contexto extraído de la URL ({url}) para responder a '{question}':\n\n{context}"
        
    except Exception as e:
        logger.error("Error en RAG Tool: %s", e)
        return f"Error técnico al procesar la página web: {str(e)}"

def get_rag_tools():
    """Devuelve las herramientas de RAG."""
    return [
        Tool(
            name="read_and_search_wiki",
            func=query_wiki_tool,
            description="Útil para extraer respuestas precisas de una página web muy larga (como una Wiki o guía). Input obligatorio: URL de la página y tu pregunta separadas por un pipe (|). Ejemplo: 'https://darksouls.wiki.fextralife.com/Margit|¿Cuáles son sus debilidades?'."
        )
    ]
