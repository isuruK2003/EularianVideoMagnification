import cv2
import numpy as np
from scipy.signal import butter, filtfilt


input_video = input("Video path: ")
output_video = input_video.split(".")[0] + "_amplified" + ".mp4"
amplification_factor = 30 
low_freq = 0.4 
high_freq = 1.0

# Load the video
cap = cv2.VideoCapture(input_video)
if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Video writer setup for saving amplified output
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

# Read all frames into a list for processing
frames = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Keep frames in color

cap.release()
frames = np.array(frames, dtype='float32')

# Apply temporal filtering to isolate vibrations within frequency bounds
def bandpass_filter(data, lowcut, highcut, fs, order=2):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    y = filtfilt(b, a, data, axis=0)
    return y

# Apply the bandpass filter to the frames to get the motion component
filtered_frames = bandpass_filter(frames, low_freq, high_freq, fps)

# Amplify the filtered frames and add back to the original frames
amplified_frames = frames + amplification_factor * filtered_frames

# Convert back to uint8 and save each frame to the output video
for amplified_frame in amplified_frames:
    amplified_frame = np.clip(amplified_frame, 0, 255)  # Clip values to ensure they stay in the 0-255 range
    amplified_frame = amplified_frame.astype('uint8')
    amplified_frame_bgr = cv2.cvtColor(amplified_frame, cv2.COLOR_RGB2BGR)
    out.write(amplified_frame_bgr)

out.release()
print("Amplified video saved as:", output_video)
