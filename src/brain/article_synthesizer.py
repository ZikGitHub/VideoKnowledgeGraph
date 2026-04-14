import ollama
import os


class ArticleSynthesizer:
    """
    Uses Ollama to turn raw video clusters 
    into structured Knowledge Articles.
    """
    def __init__(self, model="qwen3.5:2b"):
        self.model = os.getenv("OLLAMA_MODEL", model)

    def synthesize_article(self, concept_text, video_frames_desc):
        """
        Takes the semantic context and generates a deep reference article.
        """
        prompt = f"""
        You are a Knowledge Engineer. Based on the following video transcript segments 
        and visual descriptions, write a high-fidelity 'Knowledge Article' for a master 
        reference database.
        
        Transcript Context: {concept_text}
        Visual Context: {video_frames_desc}
        
        Focus on:
        1. Core Definitions.
        2. Structural Logic.
        3. Visual Layout explained in text.
        """
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content']
        except Exception as e:
            return f"Synthesis failed: {e}"

if __name__ == "__main__":
    synthesizer = ArticleSynthesizer()
    print(synthesizer.synthesize_article("Gradient Descent is an optimization algorithm.", "A graph showing a curve."))
