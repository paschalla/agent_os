import os
import glob
from typing import List, Dict, Any

class KnowledgeBaseTool:
    def __init__(self):
        # Define knowledge paths (exports from chat, and a manual knowledge folder)
        self.home = os.path.expanduser("~")
        self.search_paths = [
            os.path.join(os.getcwd(), "exports"),
            os.path.join(os.getcwd(), "knowledge"),
            os.path.join(self.home, ".andy-os", "knowledge")
        ]

    def search(self, query: str, limit: int = 3) -> str:
        """
        Search the knowledge base (markdown files) for the given query.
        Simple keyword matching for now.
        """
        results = []
        query_terms = query.lower().split()
        
        for path in self.search_paths:
            if not os.path.exists(path):
                continue
                
            # Find all .md files
            files = glob.glob(os.path.join(path, "*.md"))
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf_8', errors='ignore') as f:
                        content = f.read()
                        content_lower = content.lower()
                        
                        # Score: how many query terms are present?
                        score = sum(1 for term in query_terms if term in content_lower)
                        
                        if score > 0:
                            # snippet generation (simple: first 500 chars or context around match)
                            # context window around first match
                            first_match_idx = -1
                            for term in query_terms:
                                idx = content_lower.find(term)
                                if idx != -1:
                                    first_match_idx = idx
                                    break
                            
                            start = max(0, first_match_idx - 100)
                            end = min(len(content), first_match_idx + 400)
                            snippet = content[start:end].replace('\n', ' ')
                            
                            results.append({
                                "file": os.path.basename(file_path),
                                "score": score,
                                "snippet": f"...{snippet}..."
                            })
                except Exception as e:
                    continue

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        if not results:
            return "No relevant information found in the knowledge base."
            
        # Format output
        output = "Found the following info in Knowledge Base:\n"
        for i, res in enumerate(results[:limit]):
            output += f"{i+1}. [{res['file']}]: {res['snippet']}\n"
            
        return output

# Standalone function for tool registry
def search_knowledge_base(query: str) -> str:
    """
    Search past conversations and knowledge files for information.
    Useful for recalling facts, "what did we do yesterday?", or looking up stored notes.
    """
    kb = KnowledgeBaseTool()
    return kb.search(query)
