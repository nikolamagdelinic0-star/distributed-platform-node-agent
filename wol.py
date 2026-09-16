"""Wake-on-LAN routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from database import SessionLocal, Node
from auth import get_current_user, get_db

router = APIRouter()

@router.post("/wake/{node_id}", tags=["wol"])
def wake_node(node_id: str, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    """Send Wake-on-LAN magic packet to wake a computer."""
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    mac = node.mac_address if hasattr(node, 'mac_address') and node.mac_address else None
    
    # Send magic packet
    try:
        from wakeonlan import send_magic_packet
        if mac:
            send_magic_packet(mac)
        else:
            # Broadcast to all nodes
            send_magic_packet("FF:FF:FF:FF:FF:FF")
        return {"status": "magic_packet_sent", "node_id": node_id, "mac": mac}
    except Exception as e:
        # Fallback: manual magic packet
        try:
            import socket
            mac_bytes = bytes.fromhex((mac or "FFFFFFFFFFFF").replace(':', '').replace('-', ''))
            magic = b'\xff' * 6 + mac_bytes * 16
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic, ('255.255.255.255', 9))
            sock.close()
            return {"status": "magic_packet_sent", "node_id": node_id, "mac": mac}
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"WoL failed: {str(e2)}")

@router.get("/wake", tags=["wol"])
def wake_all_nodes(db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    """Wake all nodes in the cluster."""
    nodes = db.query(Node).filter(Node.current_status == "OFFLINE").all()
    result = []
    try:
        from wakeonlan import send_magic_packet
        for node in nodes:
            mac = node.mac_address if hasattr(node, 'mac_address') and node.mac_address else None
            if mac:
                send_magic_packet(mac)
                result.append({"node_id": node.node_id, "status": "wok_sent"})
    except Exception as e:
        pass
    return {"status": "done", "woken": result}
