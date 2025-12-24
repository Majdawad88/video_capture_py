#git clone https://github.com/Majdawad88/video_capture_py.git

from picamera2 import Picamera2
import cv2, time

# ---- Settings ----
capture_size = (1280, 720)
save_size    = (640, 480)
fps          = 20.0
path         = "output_1.avi"

print("Initializing Pi Camera...")
picam2 = Picamera2()
picam2.preview_configuration.main.size = capture_size
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

print("Starting camera...")
picam2.start()
time.sleep(0.3)

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter(path, fourcc, fps, save_size, True)

print("Recording... press Ctrl+C to stop.")
try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.flip(frame, 0)
        frame = cv2.resize(frame, save_size)
        out.write(frame)

        # --- REMOVE THESE FOR SSH ---
        # cv2.imshow('Original Stream', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        # -----------------------------
except KeyboardInterrupt:
    print("\nStopping recording...")
finally:
    out.release()
    picam2.stop()
    # cv2.destroyAllWindows() 
    print("Saved:", path)
   
    
