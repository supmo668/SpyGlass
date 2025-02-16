import json
from typing import List, Dict, Optional
import clip
import torch
from aperturedb.Utils import Utils
from aperturedb.CommonLibrary import create_connector, execute_query
from aperturedb.Constraints import Constraints
from aperturedb.Images import Images

class ApertureTools:
    def __init__(self):
        self.client = create_connector()
        self.utils = Utils(self.client)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/16", device=self.device)

    def search_similar_companies(self, description: str, limit: int = 5) -> List[Dict]:
        """Search for similar companies in ApertureDB based on description."""
        try:
            # Generate embeddings for the search description
            search_tokens = clip.tokenize([description]).to(self.device)
            search_embeddings = self.model.encode_text(search_tokens)
            
            query = [{
                "FindDescriptor": {
                    "set": "ViT-B/16",
                    "k_neighbors": limit,
                    "distances": True,
                    "vector": search_embeddings[0].tolist(),
                    "with_class": "Company",
                    "results": {
                        "all_properties": True
                    }
                }
            }]
            
            result, response, _ = execute_query(self.client, query, [])
            if result == 0 and response:
                return response[0].get("results", [])
            return []
        except Exception as e:
            print(f"Error in search_similar_companies: {str(e)}")
            return []

    def search_market_data(self, keywords: str, limit: int = 5) -> List[Dict]:
        """Search for market data and trends in ApertureDB based on keywords."""
        try:
            query = [{
                "FindEntity": {
                    "with_class": "MarketData",
                    "constraints": {
                        "keywords": ["contains", keywords]
                    },
                    "results": {
                        "limit": limit,
                        "all_properties": True
                    }
                }
            }]
            
            result, response, _ = execute_query(self.client, query, [])
            if result == 0 and response:
                return response[0].get("results", [])
            return []
        except Exception as e:
            print(f"Error in search_market_data: {str(e)}")
            return []

    async def handle_tool_call(self, tool_call) -> Optional[Dict]:
        """Handle a tool call and return the response."""
        try:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "search_similar_companies":
                return {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(self.search_similar_companies(
                        description=function_args.get("description"),
                        limit=function_args.get("limit", 5)
                    ))
                }
            elif function_name == "search_market_data":
                return {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(self.search_market_data(
                        keywords=function_args.get("keywords"),
                        limit=function_args.get("limit", 5)
                    ))
                }
            return None
        except Exception as e:
            print(f"Error handling tool call: {str(e)}")
            return None
