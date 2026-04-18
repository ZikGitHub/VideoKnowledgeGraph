
import os
from datetime import datetime



class MarkdownGenerator:
    """
    Generates GFM (GitHub Flavored Markdown) summaries.
    """
    def __init__(self, output_dir="data/outputs"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate(self, video_title, youtube_url, richness_score, concepts):
        safe_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '_')]).rstrip()
        filename = f"{safe_title}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {video_title}\n\n")
            f.write(f"- **URL:** {youtube_url}\n")
            f.write(f"- **Richness Score:** {richness_score}\n\n")
            f.write("## Table of Contents\n")
            for i, c in enumerate(concepts):
                f.write(f"- [{i+1}. Segment at {c['timestamp']:.2f}s](#segment-{i+1})\n")
            
            f.write("\n---\n\n")
            
            for i, c in enumerate(concepts):
                f.write(f"### Segment {i+1}\n")
                f.write(f"*Timestamp: {c['timestamp']:.2f}s*\n\n")
                f.write("#### Original Transcript Snippet\n")
                f.write(f"> {c['text']}\n\n")
                f.write("#### Synthesized Knowledge\n")
                f.write(f"{c.get('synthesized_article', 'No synthesis available.')}\n\n")
                f.write("---\n\n")
        
        return filepath

if __name__ == "__main__":
    test_concepts = [
        {"timestamp": 0.0, "text": "Hello world", "synthesized_article": "Intro knowledge article content..."},
        {"timestamp": 30.5, "text": "Deep learning intro", "synthesized_article": "Neural networks are models..."}
    ]
    gen = MarkdownGenerator()
    path = gen.generate("Test Video", "http://test.com", 0.95, test_concepts)
    print(f"Generated Markdown at: {path}")
