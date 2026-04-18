import os
import sys
# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.streamer import VideoStreamer
from src.ingestion.transcript_api import TranscriptFetcher
from src.ingestion.boundary_detector import BoundaryDetector
from src.embeddings.imagebind_wrapper import MultimodalKnowledgeBase
import time
import torch

def run_test_pipeline(youtube_url):
    print(f"\nStarting Pipeline Test for: {youtube_url}\n" + "="*50)

    device = "CUDA" if torch.cuda.is_available() else "CPU"
    print(f"[SYSTEM] PyTorch Compute: {device}")
    if device == "CPU":
        print("[WARNING] GPU not detected! ImageBind and embeddings will run very slowly on CPU.\n")

    # 1. Fetch Transcript
    print("Step 1: Fetching Transcript...")
    fetcher = TranscriptFetcher(youtube_url)
    transcript = fetcher.get_transcript()
    if not transcript:
        print("[Error] Failed to fetch transcript. Exiting.")
        return
    print(f"[Done] Fetched {len(transcript)} transcript segments.\n")

    # 2. Detect Semantic Boundaries
    print("Step 2: Detecting Semantic Boundaries...")
    detector = BoundaryDetector()
    text_bounds = detector.detect_textual_boundaries(transcript)
    
    # Helper to get start/duration
    get_v = lambda obj, key: getattr(obj, key) if hasattr(obj, key) else obj[key]
    last_seg = transcript[-1]
    video_end = get_v(last_seg, "start") + get_v(last_seg, "duration")

    # We add start (0) and end manually
    boundaries = sorted(list(set([0.0] + text_bounds + [video_end])))
    print(f"[Done] Found {len(boundaries)-1} Semantic Segments.\n")
    print(f"Boundaries (seconds): {boundaries}\n")

    # 3. Setup Knowledge Base (ChromaDB)
    print("Step 3: Initializing ChromaDB...")
    kb = MultimodalKnowledgeBase()
    print("[Done] Knowledge Base Ready.\n")

    # 4. Process the first 2 segments (Prototyping Run)
    print("Step 4: Processing First 2 Semantic Segments...")
    # Initialize streamer
    streamer = VideoStreamer(youtube_url, sampling_rate=0.5)
    
    # Simple loop to process segments
    for i in range(len(boundaries) - 1):
        if i >= 2: break # Only test 2 segments
        
        start = boundaries[i]
        end = boundaries[i+1]
        print(f"--- Segment {i+1} [{start:.2f}s - {end:.2f}s] ---")
        
        # Get transcript text for this segment
        seg_text = " ".join([get_v(seg, 'text') for seg in transcript if start <= get_v(seg, 'start') < end])
        print(f"Text Content: {seg_text[:100]}...")
        
        # Mock frame capture
        print(f"Encoding Concept '{seg_text[:20]}...' into Vector Space...")
        kb.add_concept(i+1, [], seg_text, start)
        print(f"[Done] Segment {i+1} Encoded.\n")

    # 5. Semantic Query Test
    print("Step 5: Testing Semantic Search...")
    query = "the basic building blocks of transformers"
    print(f"Querying for: '{query}'")
    
    # We must embed the query manually because Chroma expects 1024-dim vectors
    query_vector = kb.engine.embed_text(query)

    results = kb.collection.query(
        query_embeddings=[query_vector.tolist()], 
        n_results=1
    )
    
    if results['documents']:
        print(f"\n[Success] Search Result Found!")
        print(f"Document: {results['documents'][0][0][:200]}...")
        print(f"Metadata: {results['metadatas'][0][0]}")
        print("\n[Done] PIPELINE TEST SUCCESSFUL.")
    else:
        print("[Error] No matching knowledge found.")

if __name__ == "__main__":
    TEST_URL = "https://www.youtube.com/watch?v=wjZofJX0v4M" # Inside Transformers
    run_test_pipeline(TEST_URL)
