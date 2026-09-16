"""Job scheduling and management routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import logging
logger = logging.getLogger("jobs")
import json
import requests

from database import SessionLocal, Job, JobNodeMapping, Node
from auth import get_current_user, check_permission, get_db
from config import JobState, Priority

router = APIRouter()

CONTROLLER_URL = "http://localhost:8000"


@router.post("/", response_model=Dict[str, Any])
def submit_job(
    name: str,
    task_type: str = "compute",
    requirements: Optional[Dict] = None,
    priority: str = "NORMAL",
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    if requirements is None:
        requirements = {}
    if priority not in [p.value for p in Priority]:
        raise HTTPException(status_code=400, detail="Invalid priority")
    job = Job(
        name=name,
        task_type=task_type,
        requirements=requirements,
        priority=priority,
        description=description,
        user_id=current_user.id,
        status="QUEUED"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    # Try to distribute to nodes
    _distribute_job(job, db)
    return {"message": "Job submitted", "job_id": job.job_id, "status": job.status}


def _distribute_job(job: Job, db: Session):
    """Distribute a job to available nodes."""
    nodes = db.query(Node).filter(Node.current_status == "ONLINE").all()
    if not nodes:
        logger.warning(f"No online nodes to distribute job {job.job_id}")
        return
    # Assign to first available node
    node = nodes[0]
    mapping = JobNodeMapping(job_id=job.job_id, node_id=node.node_id)
    db.add(mapping)
    node.current_status = "BUSY"
    db.commit()
    job.status = "RUNNING"
    db.commit()
    # Notify node via HTTP
    try:
        requests.post(
            f"http://{node.hostname}:8001/api/v1/jobs/execute",
            json={"job_id": job.job_id, "task_type": job.task_type, "requirements": job.requirements},
            timeout=5
        )
    except Exception as e:
        logger.error(f"Failed to notify node {node.node_id}: {e}")


@router.post("/{job_id}/execute")
def execute_job(job_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    """Execute a job — called by nodes."""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = "RUNNING"
    db.commit()
    return {"message": f"Job {job_id} executing on node"}


@router.get("/{job_id}", response_model=Dict[str, Any])
def get_job(job_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not check_permission(current_user, "manage_all_jobs") and job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    return job.to_dict()


@router.post("/{job_id}/cancel")
def cancel_job(job_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not check_permission(current_user, "manage_all_jobs") and job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    job.status = "CANCELLED"
    db.commit()
    return {"message": "Job cancelled"}


@router.post("/{job_id}/pause")
def pause_job(job_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "RUNNING":
        raise HTTPException(status_code=400, detail="Job is not running")
    job.status = "PAUSED"
    db.commit()
    return {"message": "Job paused"}


@router.post("/{job_id}/resume")
def resume_job(job_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "PAUSED":
        raise HTTPException(status_code=400, detail="Job is not paused")
    job.status = "QUEUED"
    db.commit()
    return {"message": "Job resumed"}


@router.get("/cluster/summary")
def cluster_summary(db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    nodes = db.query(Node).filter(Node.current_status.in_(["ONLINE", "BUSY", "IDLE"])).all()
    total_cpu = sum(n.cpu_cores for n in nodes)
    total_ram = sum(n.total_ram for n in nodes)
    total_gpu = sum(1 for n in nodes if n.gpu_model)
    total_vram = sum(n.gpu_vram for n in nodes)
    total_storage = sum(n.storage_capacity for n in nodes)
    online = sum(1 for n in nodes if n.current_status == "ONLINE")
    busy = sum(1 for n in nodes if n.current_status == "BUSY")
    idle = sum(1 for n in nodes if n.current_status == "IDLE")
    offline = sum(1 for n in nodes if n.current_status == "OFFLINE")
    return {
        "cluster": {
            "total_nodes": len(nodes),
            "online": online,
            "busy": busy,
            "idle": idle,
            "offline": offline,
            "total_cpu_cores": total_cpu,
            "total_ram_bytes": total_ram,
            "total_ram_gb": round(total_ram / (1024**3), 2),
            "total_gpus": total_gpu,
            "total_vram_bytes": total_vram,
            "total_vram_gb": round(total_vram / (1024**3), 2),
            "total_storage_bytes": total_storage,
            "total_storage_tb": round(total_storage / (1024**4), 2)
        }
    }
