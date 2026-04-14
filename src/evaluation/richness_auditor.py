import ollama
from typing import List, Dict
import os

class RichnessAuditor:
    """
    Evaluates the richness and accuracy of the extracted knowledge 
    relative to the original transcript.
    """
    def __init__(self, model="qwen3.5:2b"):
        self.model = os.getenv("OLLAMA_MODEL", model)

    def audit_coverage(self, transcript_text: str, knowledge_base_summary: str):
        """
        Uses LLM-as-a-Judge to measure information coverage.
        Returns a dictionary with 'score' and 'analysis'.
        """
        prompt = f"""
        Act as a Knowledge Auditor. Compare the following two sources:
        
        SOURCE 1 (Base Transcript):
        {transcript_text}
        
        SOURCE 2 (Extracted Knowledge Base):
        {knowledge_base_summary}
        
        Evaluate only the extraction quality. Return YOUR RESPONSE IN JSON FORMAT:
        {{
            "score": <float between 0.0 and 1.0>,
            "hallucinations": <list of any fabricated facts>,
            "missing_atoms": <list of core concepts missed>,
            "reasoning": <brief explanation>
        }}
        """
        
        try:
            response = ollama.chat(model=self.model, format='json', messages=[
                {'role': 'user', 'content': prompt}
            ])
            import json
            return json.loads(response['message']['content'])
        except Exception as e:
            print(f"Audit failed: {e}")
            return {"score": 0.0, "reasoning": f"Audit error: {e}"}

if __name__ == "__main__":
    auditor = RichnessAuditor()
    print(auditor.audit_coverage("The sun is hot.", "Node: Sun, Property: Heat."))
