"""Node management routes."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from database import SessionLocal, Node, NodeGroup, NodeGroupMapping
from auth import get_current_user, check_permission, get_db
from config import NodeState

router = APIRouter()



@router.get("/", response_model=Dict[str, Any])
def list_nodes(
    status: Optional[str] = None,
    search: Optional[str] = None,
    group_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    query = db.query(Node)
    if status:
        query = query.filter(Node.current_status == status)
    if search:
        query = query.filter(Node.hostname.ilike(f"%{search}%"))
    if group_id:
        mapping = db.query(NodeGroupMapping).filter(NodeGroupMapping.group_id == group_id).all()
        node_ids = [m.node_id for m in mapping]
        query = query.filter(Node.id.in_(node_ids))
    nodes = query.all()
    return {"nodes": [n.to_dict() for n in nodes], "total": len(nodes)}


@router.get("/{node_id}", response_model=Dict[str, Any])
def get_node(node_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node.to_dict()


@router.put("/{node_id}/status")
def update_node_status(node_id: str, status: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    if not check_permission(current_user, "configure_cluster"):
        raise HTTPException(status_code=403, detail="Permission denied")
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    valid_states = [s.value for s in NodeState]
    if status not in valid_states:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_states}")
    node.current_status = status
    db.commit()
    return {"message": f"Node status updated to {status}"}


@router.put("/{node_id}/approve")
def approve_node(node_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    if not check_permission(current_user, "configure_cluster"):
        raise HTTPException(status_code=403, detail="Permission denied")
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.current_status = "ONLINE"
    db.commit()
    return {"message": f"Node {node_id} approved"}


@router.put("/{node_id}/reject")
def reject_node(node_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    if not check_permission(current_user, "configure_cluster"):
        raise HTTPException(status_code=403, detail="Permission denied")
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.current_status = "UNAUTHORIZED"
    db.commit()
    return {"message": f"Node {node_id} rejected"}


@router.delete("/{node_id}")
def remove_node(node_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    if not check_permission(current_user, "configure_cluster"):
        raise HTTPException(status_code=403, detail="Permission denied")
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(node)
    db.commit()
    return {"message": f"Node {node_id} removed"}


@router.post("/{node_id}/rotate-credentials")
def rotate_credentials(node_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    if not check_permission(current_user, "configure_cluster"):
        raise HTTPException(status_code=403, detail="Permission denied")
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    import secrets
    node.credentials = secrets.token_hex(32)
    db.commit()
    return {"message": "Credentials rotated", "credentials": node.credentials}


@router.post("/heartbeat")
async def node_heartbeat(body: Request, db: Session = Depends(get_db)):
    try:
        data = await body.json()
        node_id = data.get("node_id")
        node = db.query(Node).filter(Node.node_id == node_id).first()
        if node:
            node.last_heartbeat = datetime.now(timezone.utc)
            node.last_seen = datetime.now(timezone.utc)
            node.current_status = data.get("status", "ONLINE")
            db.commit()
        else:
            hardware = data.get("hardware", {})
            node = Node(
                node_id=node_id,
                hostname=hardware.get("cpu_model", "Unknown"),
                os_name=hardware.get("os_name", "Unknown"),
                os_version=hardware.get("os_version", "Unknown"),
                cpu_model=hardware.get("cpu_model", "Unknown"),
                cpu_cores=hardware.get("cpu_cores", 1),
                logical_processors=hardware.get("logical_processors", 1),
                total_ram=hardware.get("total_ram", 0),
                current_status="ONLINE",
                agent_version=data.get("agent_version", "1.0.0"),
                capabilities={}
            )
            db.add(node)
            db.commit()
        return {"status": "ok", "node_id": node_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics")
async def node_metrics(body: Request, db: Session = Depends(get_db)):
    try:
        data = await body.json()
        node_id = data.get("node_id")
        metrics = data.get("metrics", {})
        node = db.query(Node).filter(Node.node_id == node_id).first()
        if node:
            node.cpu_utilization = metrics.get("cpu_utilization", node.cpu_utilization)
            node.available_ram = metrics.get("available_ram", node.available_ram)
            node.gpu_utilization = metrics.get("gpu_utilization", node.gpu_utilization)
            node.gpu_temperature = metrics.get("gpu_temperature", node.gpu_temperature)
            node.current_status = metrics.get("status", node.current_status)
            node.current_workload = metrics.get("current_workload", node.current_workload)
            node.total_ram = metrics.get("total_ram", node.total_ram)
            node.free_storage = metrics.get("free_storage", node.free_storage)
            node.network_latency = metrics.get("network_latency", node.network_latency)
            node.network_bandwidth_estimate = metrics.get("network_bandwidth_estimate", node.network_bandwidth_estimate)
            node.last_seen = datetime.now(timezone.utc)
            db.commit()
        return {"status": "ok", "node_id": node_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
