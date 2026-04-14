import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.graph_builder import app
import time

def run_sentinel(youtube_url):
    print(f"\nV2K Sentinel: Starting Autonomous Knowledge Extraction")
    print("="*60)
    
    inputs = {
        "youtube_url": youtube_url,
        "concepts": [],
        "transcript": [],
        "status": "starting"
    }
    
    start_time = time.time()
    
    # Get the final state
    result = app.invoke(inputs)
    
    end_time = time.time()
    print("="*60)
    print(f"Extraction Complete in {end_time - start_time:.2f} seconds.")
    print(f"Video Title: {result.get('video_title')}")
    print(f"Concepts Captured: {len(result.get('concepts', []))}")
    
    # Audit Score
    audit = result.get('audit_results', {})
    score = audit.get('score', 0.0)
    print(f"Richness Audit Score: {score:.2f}/1.00")
    print(f"Audit Reasoning: {audit.get('reasoning', 'No reasoning provided.')}")
    
    print("="*60)
    print("\nYou can now download the PDF/Markdown via the FastAPI backend.")

if __name__ == "__main__":
    TEST_URL = "https://www.youtube.com/watch?v=wjZofJX0v4M" # Transformer intro
    run_sentinel(TEST_URL)
