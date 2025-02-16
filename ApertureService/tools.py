from typing import List, Dict, Optional, Any
import json
import os
from langchain_community.vectorstores.aperturedb import ApertureDB
from langchain_core.embeddings import Embeddings
import requests
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document

class TogetherEmbeddings(Embeddings):
    def __init__(self, api_key: str, model: str = "togethercomputer/m2-bert-80M-8k-retrieval"):
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.together.xyz/v1/embeddings"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents."""
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "input": texts
                }
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as e:
            print(f"Error in embed_documents: {str(e)}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "input": [text]
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            print(f"Error in embed_query: {str(e)}")
            raise

class ApertureTools:
    def __init__(self):
        # Parse ApertureDB configuration from environment
        aperturedb_config = json.loads(os.environ['APERTUREDB_JSON'])
        
        # Initialize Together AI embeddings
        self.embeddings = TogetherEmbeddings(
            api_key=os.environ['TOGETHERAI_API_KEY'],
            model="togethercomputer/m2-bert-80M-8k-retrieval"  # Together AI's embedding model
        )
        
        # Initialize ApertureDB vector store
        self.vectorstore = ApertureDB(
            embeddings=self.embeddings,
            descriptor_set="spy_glass",
            dimensions=768  # m2-bert-80M-8k-retrieval outputs 768-dimensional embeddings
        )
        
        # Create the retriever tool with MMR search
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",  # Use Maximum Marginal Relevance
            search_kwargs={
                "k": 5,
                "fetch_k": 20,  # Fetch more documents for diversity
                "lambda_mult": 0.7  # Balance between relevance and diversity
            }
        )
        
        # Create the LangChain tool
        self.tool = create_retriever_tool(
            self.retriever,
            name="search_business_reports",
            description="Search for relevant business reports and market analysis. Use this for finding information about market trends, competitor analysis, and business opportunities."
        )

    def get_tool(self):
        """Get the LangChain retriever tool."""
        return self.tool

    async def add_document(self, document: Document):
        """Add a new document to the vector store using async method."""
        try:
            await self.vectorstore.aadd_documents([document])
            return True
        except Exception as e:
            raise Exception(f"Failed to add document: {str(e)}")

    async def search_similar_documents(self, query: str, k: int = 5):
        """Search for similar documents with relevance scores."""
        try:
            docs = await self.vectorstore.asimilarity_search_with_relevance_scores(query, k=k)
            return docs
        except Exception as e:
            raise Exception(f"Failed to search documents: {str(e)}")

    async def delete_documents(self, ids: Optional[List[str]] = None):
        """Delete documents from the vector store."""
        try:
            await self.vectorstore.adelete(ids=ids)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete documents: {str(e)}")

    def handle_tool_call(self, tool_call):
        """Handle a tool call and return the response."""
        try:
            return self.tool.invoke(tool_call)
        except Exception as e:
            raise Exception(f"Failed to handle tool call: {str(e)}")
