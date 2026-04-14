import os
import sys
from typing import Annotated, List, TypedDict, Dict
from langgraph.graph import StateGraph, END
import operator

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.ingestion.streamer import VideoStreamer
from src.ingestion.transcript_api import TranscriptFetcher
from src.ingestion.boundary_detector import BoundaryDetector
from src.embeddings.imagebind_wrapper import MultimodalKnowledgeBase
from src.brain.article_synthesizer import ArticleSynthesizer
from src.evaluation.richness_auditor import RichnessAuditor
from src.brain.local_graph import LocalGraphBuilder

# Define the state of our knowledge extraction graph
class GraphState(TypedDict):
    youtube_url: str
    video_title: str
    transcript: List[Dict]
    boundaries: List[float]
    concepts: Annotated[List[Dict], operator.add] # List of dicts with 'text', 'timestamp', 'synthesized_article'
    audit_results: Dict
    status: str

# Node Implementations
def ingest_video_node(state: GraphState):
    print(f"--- Node: Ingesting [{state['youtube_url']}] ---")
    fetcher = TranscriptFetcher(state['youtube_url'])
    transcript = fetcher.get_transcript()
    # Mocking title for now or fetching from ydl later
    title = "Video Analysis"
    return {"transcript": transcript, "video_title": title, "status": "ingested"}

def detect_boundaries_node(state: GraphState):
    print("--- Node: Detecting Semantic Boundaries ---")
    detector = BoundaryDetector()
    text_bounds = detector.detect_textual_boundaries(state['transcript'])
    
    # Helper to get video end
    get_v = lambda obj, key: getattr(obj, key) if hasattr(obj, key) else obj[key]
    last_seg = state['transcript'][-1]
    video_end = get_v(last_seg, "start") + get_v(last_seg, "duration")
    
    boundaries = sorted(list(set([0.0] + text_bounds + [video_end])))
    return {"boundaries": boundaries, "status": "boundaries_detected"}

def embed_and_synthesize_node(state: GraphState):
    print("--- Node: Embedding & Synthesizing Knowledge ---")
    kb = MultimodalKnowledgeBase()
    synthesizer = ArticleSynthesizer()
    
    get_v = lambda obj, key: getattr(obj, key) if hasattr(obj, key) else obj[key]
    new_concepts = []
    
    # Process segments
    for i in range(len(state['boundaries']) - 1):
        start = state['boundaries'][i]
        end = state['boundaries'][i+1]
        
        # Get text for this segment
        seg_text = " ".join([get_v(seg, 'text') for seg in state['transcript'] if start <= get_v(seg, 'start') < end])
        
        # 1. Synthesize Article (Ollama)
        article = synthesizer.synthesize_article(seg_text, "Visual analysis pending...")
        
        # 2. Embed into Chroma (Mocking frames for now)
        kb.add_concept(i, [], seg_text, start)
        
        new_concepts.append({
            "id": i,
            "timestamp": start,
            "text": seg_text,
            "synthesized_article": article
        })
        
    # 3. Create Local Relationship Graph
    graph_builder = LocalGraphBuilder()
    vid_id = "".join([c for c in state['youtube_url'] if c.isalnum()])[-10:]
    graph_builder.build_graph(vid_id, new_concepts)
        
    return {"concepts": new_concepts, "status": "processed"}

def audit_richness_node(state: GraphState):
    print("--- Node: Auditing Richness ---")
    auditor = RichnessAuditor()
    
    full_transcript = " ".join([str(s) for s in state['transcript']])
    knowledge_summary = "\n\n".join([f"Segment at {c['timestamp']}s: {c['synthesized_article']}" for c in state['concepts']])
    
    audit_results = auditor.audit_coverage(full_transcript, knowledge_summary)
    return {"audit_results": audit_results, "status": "audited"}

# Build Workflow
workflow = StateGraph(GraphState)

workflow.add_node("ingest", ingest_video_node)
workflow.add_node("boundaries", detect_boundaries_node)
workflow.add_node("process", embed_and_synthesize_node)
workflow.add_node("audit", audit_richness_node)

workflow.set_entry_point("ingest")
workflow.add_edge("ingest", "boundaries")
workflow.add_edge("boundaries", "process")
workflow.add_edge("process", "audit")
workflow.add_edge("audit", END)

app = workflow.compile()
