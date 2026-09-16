"""Screen capture module for remote desktop."""
import json
import logging
from PIL import Image
import io
import numpy as np

logger = logging.getLogger("screen-capture")

class ScreenCapture:
    def capture(self):
        """Capture the screen as PNG bytes."""
        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                img = np.array(sct.grab(monitor))
                pil_img = Image.fromarray(img)
                buf = io.BytesIO()
                pil_img.save(buf, format='PNG')
                return buf.getvalue()
        except Exception as e:
            logger.error(f"Capture failed: {e}")
            return None
    
    def get_resolution(self):
        """Get screen resolution."""
        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                return {"width": monitor["width"], "height": monitor["height"]}
        except:
            return {"width": 1920, "height": 1080}
