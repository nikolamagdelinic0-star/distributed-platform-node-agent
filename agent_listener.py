"""Job execution listener for the node agent. Runs on port 8001."""
import subprocess
import sys
import os
import json
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-listener")

class JobHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        job_id = data.get('job_id')
        task_type = data.get('task_type', 'compute')
        requirements = data.get('requirements', {})
        
        logger.info(f"Executing job {job_id}: {task_type}")
        
        # Execute the job (placeholder — extend for actual tasks)
        result = self.execute_task(task_type, requirements)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "completed", "job_id": job_id, "result": result}).encode())
    
    def execute_task(self, task_type, requirements):
        """Execute a computing task."""
        if task_type == 'compute':
            return {"status": "completed", "message": "Compute task done"}
        elif task_type == 'ai_training':
            return {"status": "completed", "message": "AI training done"}
        else:
            return {"status": "completed", "message": f"Task {task_type} done"}
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8001), JobHandler)
    logger.info("Agent listener running on port 8001")
    server.serve_forever()


# Add MAC address endpoint
class MacHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        import uuid
        mac = ':'.join(('{:012x}'.format(uuid.getnode())[i:i+2] for i in range(0, 12, 2)))
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"mac_address": mac}).encode())
    
    def log_message(self, format, *args):
        pass

# Add to the handler class
JobHandler.do_GET = MacHandler.do_GET
