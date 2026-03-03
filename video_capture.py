

# Installation Command:
# !git clone https://github.com/Majdawad88/video_capture_py.git

# --- KEYBOARD MAPPING ---
# '1' : Reset to original view
# '2' : Remove Blue Channel (No Blue)
# '3' : Rotate Image 90 Degrees Clockwise
# '4' : Apply Threshold Mask & Draw Bounding Box
# '5' : Segment Gold/Yellow using HSV Mask
# 'q' : Stop Recording and Exit
# ------------------------

import cv2
import time
import numpy as np
try:
    from picamera2 import Picamera2
except ImportError:
    print("Picamera2 not found. Running in simulation mode (check Pi connection).")

# ---- Configuration ----
CAPTURE_SIZE = (1280, 720)
SAVE_SIZE    = (640, 480)
FPS          = 20.0
OUTPUT_PATH  = "output_1.avi"

def run_video_capture():
    print("Initializing Camera for Recording...")
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = CAPTURE_SIZE
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")

    print("Starting camera...")
    picam2.start()
    time.sleep(0.3) 

    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, SAVE_SIZE, True)

    mode = '1' # Default mode is original
    print("Recording... Press 'q' to stop.")

    try:
        while True:
            # Capture live frame
            original_frame = picam2.capture_array()
            
            # --- Process Keyboard Input ---
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                mode = chr(key)

            # Create a copy to manipulate so we don't destroy the original data
            processed_frame = original_frame.copy()

            # --- Transformation Modes ---
            if mode == '2':
                # No Blue: Set channel index 0 (Blue in BGR) to 0
                processed_frame[:, :, 0] = 0
            
            elif mode == '3':
                # Rotate 90 Degrees Clockwise
                processed_frame = cv2.rotate(processed_frame, cv2.ROTATE_90_CLOCKWISE)
            
            elif mode == '4':
                # Masking & Bounding Box
                gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
                coords = np.column_stack(np.where(mask > 0))
                if coords.size > 0:
                    x, y, w, h = cv2.boundingRect(coords)
                    # Draw Green Rectangle (y,x used because boundingbox returns coordinates relative to array)
                    cv2.rectangle(processed_frame, (y, x), (y + h, x + w), (0, 255, 0), 2)
            
            elif mode == '5':
                # HSV Gold/Yellow Segmentation
                hsv = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2HSV)
                lower = np.array([20, 100, 100]) 
                upper = np.array([35, 255, 255])
                mask = cv2.inRange(hsv, lower, upper)
                # Bitwise-AND to show only the detected color
                processed_frame = cv2.bitwise_and(processed_frame, processed_frame, mask=mask)

            # Ensure frame is resized correctly for saving
            display_frame = cv2.resize(processed_frame, SAVE_SIZE)

            # --- Add "RECORDING" Label ---
            # Draw a red dot and text at the top
            cv2.circle(display_frame, (30, 30), 10, (0, 0, 255), -1) # Red Circle
            cv2.putText(display_frame, "REC", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(display_frame, f"MODE: {mode}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            # Write frame to file
            out.write(display_frame)

            # Show the live stream
            cv2.imshow('Recording Stream', display_frame)

    except KeyboardInterrupt:
        print("\nRecording manually stopped.")
    finally:
        out.release()
        picam2.stop()
        cv2.destroyAllWindows()
        print(f"Video saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    run_video_capture()


#To view the image in Linux terminal:
# vlc output_1.avi
   
    
