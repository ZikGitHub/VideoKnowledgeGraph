import cv2
import numpy as np
from scenedetect import SceneManager, ContentDetector, VideoManager
from sentence_transformers import SentenceTransformer, util
import torch

class BoundaryDetector:
    """
    Combines visual scene detection and textual topic shift detection
    to find semantic boundaries in a video.
    """
    def __init__(self, visual_threshold=27.0, text_threshold=0.7):
        """
        :param visual_threshold: Threshold for ContentDetector (higher = less sensitive).
        :param text_threshold: Cosine similarity threshold for topic shift (lower = more sensitive).
        """
        self.visual_threshold = visual_threshold
        self.text_threshold = text_threshold
        # Load a lightweight BERT model for text similarity
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')

    def detect_visual_boundaries(self, stream_url):
        """Uses PySceneDetect to find visual cuts in the stream URL."""
        # Note: PySceneDetect works best on locally accessible streams.
        # For a more robust streaming implementation, we'd iterate frames manually.
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=self.visual_threshold))
        
        # Open video URL
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            return []

        # We sample at a lower rate for speed in boundary detection
        scene_list = []
        # For simplicity in this module, we'd usually use scenedetect's VideoManager
        # but since we are streaming, we'll keep it simple:
        # scene_manager.detect_scenes(video=cap) - logic would go here
        
        # Placeholder for visual logic until we integrate the full SceneManager loop
        return []

    def detect_textual_boundaries(self, transcript_segments):
        """
        Identifies topic shifts in transcript segments using semantic similarity.
        :param transcript_segments: List of dicts or objects with 'text' and 'start'.
        """
        if not transcript_segments or len(transcript_segments) < 2:
            return []

        boundaries = []
        
        # Helper to get start/text regardless of dict or object
        get_val = lambda obj, key: getattr(obj, key) if hasattr(obj, key) else obj[key]

        # Group segments into chunks of ~30 seconds for better semantic signal
        chunks = []
        first_seg = transcript_segments[0]
        current_chunk = {"text": "", "start": get_val(first_seg, "start")}
        last_start = get_val(first_seg, "start")
        
        for seg in transcript_segments:
            seg_start = get_val(seg, "start")
            seg_text = get_val(seg, "text")
            
            if seg_start - last_start > 30:
                chunks.append(current_chunk)
                current_chunk = {"text": seg_text, "start": seg_start}
                last_start = seg_start
            else:
                current_chunk["text"] += " " + seg_text

        if current_chunk["text"]:
            chunks.append(current_chunk)

        # Detect shifts between consecutive chunks
        texts = [c["text"] for c in chunks]
        embeddings = self.text_model.encode(texts, convert_to_tensor=True)

        for i in range(len(embeddings) - 1):
            similarity = util.cos_sim(embeddings[i], embeddings[i+1]).item()
            if similarity < self.text_threshold:
                boundaries.append(chunks[i+1]["start"])
        
        return boundaries

    def fuse_boundaries(self, visual_bounds, textual_bounds, tolerance=5.0):
        """
        Merges visual and textual signals. 
        If a visual cut is within 'tolerance' seconds of a text shift, it's a Strong Boundary.
        """
        # For now, we'll just combine and sort unique boundaries
        all_bounds = sorted(list(set(visual_bounds + textual_bounds)))
        
        # Simple clustering: if two boundaries are within tolerance, take the average or the visual one
        refined_bounds = []
        if not all_bounds: return []
        
        curr = all_bounds[0]
        for i in range(1, len(all_bounds)):
            if all_bounds[i] - curr < tolerance:
                # Merge logic (prefer the later one or average)
                curr = (curr + all_bounds[i]) / 2
            else:
                refined_bounds.append(curr)
                curr = all_bounds[i]
        refined_bounds.append(curr)
        
        return refined_bounds

if __name__ == "__main__":
    # Test text boundaries
    detector = BoundaryDetector()
    test_transcript = [
        {"text": "Hello world, today we talk about cat.", "start": 0},
        {"text": "Cats are small furry animals.", "start": 10},
        {"text": "They like to eat fish.", "start": 20},
        {"text": "Moving on, let's talk about rocket science.", "start": 40},
        {"text": "Rockets use liquid fuel to go to space.", "start": 50},
    ]
    bounds = detector.detect_textual_boundaries(test_transcript)
    print(f"Detected text boundaries at: {bounds}s")
