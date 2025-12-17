
from picamera2 import Picamera2
import cv2, time

# ---- Settings ----
capture_size = (1280, 720)     # sensor stream size from PiCam
save_size    = (640, 480)      # output video size to match your original
fps          = 20.0
path   = "output_1.avi"

print("Initializing Pi Camera…")
picam2 = Picamera2()

# Configure a simple RGB video stream
picam2.preview_configuration.main.size = capture_size
picam2.preview_configuration.main.format = "RGB888"  # PiCam gives RGB
picam2.configure("preview")

print("Starting camera…")
picam2.start()
time.sleep(0.3)  # short warm-up

# ---- VideoWriter  ----
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter(path, fourcc, fps, save_size, True)

# ---- Main loop ----
print("Recording… press 'q' to quit.")
try:
    while True:
        # Grab a frame from PiCamera2 (RGB888)
        frame = picam2.capture_array()

        # Flip vertically
        frame = cv2.flip(frame, 0)

        # Resize for saving/display to 640x480
        frame = cv2.resize(frame, save_size)

        # Write to files
        out.write(frame)

        # Show the stream
        cv2.imshow('Original Stream', frame)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # ---- Cleanup ----
    out.release()
    picam2.stop()
    cv2.destroyAllWindows()
    print("Saved:", path)
