import json
import os
from typing import List, Dict

class LocalGraphBuilder:
    """
    Builds a lightweight JSON-based Graph mapping relationships between Semantic Segments.
    Useful for local prototyping before scaling to Neo4j.
    """
    def __init__(self, output_dir="data/graph"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def build_graph(self, video_id: str, concepts: List[Dict]):
        """
        Takes sequential concepts and infers basic relationships (e.g., 'FOLLOWS', 'RELATES_TO').
        """
        graph = {
            "video_id": video_id,
            "nodes": [],
            "edges": []
        }

        # Identify Nodes
        for i, concept in enumerate(concepts):
            node = {
                "id": f"seg_{concept['id']}",
                "label": "Segment",
                "properties": {
                    "timestamp": concept["timestamp"],
                    "summary_preview": concept["synthesized_article"][:100] + "..." if concept.get("synthesized_article") else "",
                }
            }
            graph["nodes"].append(node)

        # Build Sequential Relationships (FOLLOWS)
        for i in range(len(concepts) - 1):
            source = f"seg_{concepts[i]['id']}"
            target = f"seg_{concepts[i+1]['id']}"
            edge = {
                "source": source,
                "target": target,
                "relationship": "FOLLOWS",
                "weight": 1.0 # Base temporal weight
            }
            graph["edges"].append(edge)

        # Save to JSON
        filename = os.path.join(self.output_dir, f"{video_id}_graph.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=4)
        
        return filename

if __name__ == "__main__":
    test_concepts = [
        {"id": 0, "timestamp": 0.0, "synthesized_article": "Intro"},
        {"id": 1, "timestamp": 30.0, "synthesized_article": "Details"}
    ]
    builder = LocalGraphBuilder()
    path = builder.build_graph("test_video", test_concepts)
    print(f"Graph saved to {path}")
