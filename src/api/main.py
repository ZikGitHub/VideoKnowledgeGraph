from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import sys
import os
from typing import Dict

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.brain.graph_builder import app as graph_app
from src.api.generators import MarkdownGenerator

api = FastAPI(title="V2K Sentinel API", description="Vision-to-Knowledge Universal Engine")

# Storage for job states (In-memory for prototype)
jobs: Dict[str, Dict] = {}

class VideoRequest(BaseModel):
    youtube_url: str

@api.get("/")
def read_root():
    return {"status": "V2K Sentinel is online", "version": "1.0.0"}

@api.post("/extract")
def extract_knowledge(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = "".join([c for c in request.youtube_url if c.isalnum()])[-10:]
    jobs[job_id] = {"status": "starting", "url": request.youtube_url}
    
    def run_graph(jid, url):
        try:
            inputs = {"youtube_url": url, "concepts": [], "transcript": []}
            result = graph_app.invoke(inputs)
            jobs[jid].update({
                "status": "completed",
                "video_title": result.get("video_title", "Video Analysis"),
                "richness_score": result.get("audit_results", {}).get("score", 0.0),
                "concepts": result.get("concepts", []),
                "audit": result.get("audit_results", {})
            })
        except Exception as e:
            jobs[jid].update({"status": "failed", "error": str(e)})

    background_tasks.add_task(run_graph, job_id, request.youtube_url)
    return {"job_id": job_id, "message": "Extraction started."}

@api.get("/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]



@api.get("/download/md/{job_id}")
def download_md(job_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not ready")
    
    job = jobs[job_id]
    gen = MarkdownGenerator()
    path = gen.generate(job["video_title"], job["url"], job["richness_score"], job["concepts"])
    return FileResponse(path, filename=os.path.basename(path), media_type='text/markdown')



if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
