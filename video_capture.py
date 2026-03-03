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
# CAPTURE_SIZE: The input resolution (1280 x 720). The camera captures in HD for better processing detail.
CAPTURE_SIZE = (1280, 720)
# SAVE_SIZE: The output resolution (640 x 480). The video is shrunk to this size to save storage space.
SAVE_SIZE    = (640, 480)
# FPS: Frames Per Second ($20.0$). This determines how smooth the video playback will be.
FPS          = 20.0
# OUTPUT_PATH: The file name (output_1.avi). It sets the name and format of the final saved video.
OUTPUT_PATH  = "output_1.avi"

def run_video_capture():
    print("Initializing Camera for Recording...")
    # Initialize the PiCamera2 object to interface with the camera
    picam2 = Picamera2()
    # Set the input resolution to 1280x720 (HD)
    picam2.preview_configuration.main.size = CAPTURE_SIZE
    # Set the pixel format to standard 24-bit RGB
    picam2.preview_configuration.main.format = "RGB888"
    # # Apply the settings and prepare the camera for the live stream
    picam2.configure("preview")

    print("Starting camera...")
    picam2.start()
    time.sleep(0.3)

    # Define codec and create VideoWriter object
    # Set the video codec to MJPEG for saving the file
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    # Initialize the video writer with file path, codec, speed, size, and color mode
    out = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, SAVE_SIZE, True)

    # Set the initial processing state to the 'original' camera view
    mode = '1' # Default mode is original
    print("Recording... Press 'q' to stop.")

    try:
        while True:
            # Pull the current image from the camera sensor as a NumPy array
            original_frame = picam2.capture_array()

            # Check for a keyboard press every 1ms and mask the result for compatibility
            key = cv2.waitKey(1) & 0xFF
            # Exit the recording loop if the 'q' key is pressed
            if key == ord('q'):
                break
            # Switch the processing mode if keys 1 through 5 are pressed
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
                # Convert the image to grayscale to simplify pixel intensity analysis
                gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                # Create a black-and-white mask where pixels brighter than 200 become white (255)
                _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
                # Find the row and column indices of all white pixels and stack them into a coordinate list
                coords = np.column_stack(np.where(mask > 0))
                # Check if any white pixels were detected before attempting to draw
                if coords.size > 0:
                   # Calculate the smallest vertical rectangle that encloses all detected pixels
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

            # Resize the processed image to 640x480 to match the predefined video saving dimensions
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
        # Finalize and close the video file to ensure it is saved correctly to disk
        out.release()
        # Power down the camera sensor and stop the background capture process
        picam2.stop()
        # Close all active OpenCV GUI windows and free up system memory
        cv2.destroyAllWindows()
        print(f"Video saved to: {OUTPUT_PATH}")
# Check if the script is being run directly (not imported) and start the recording function
if __name__ == "__main__":
    run_video_capture()


#To view the image in Linux terminal:
# vlc output_1.avi
