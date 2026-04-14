import cv2
import yt_dlp
import os
import time
from datetime import datetime

class VideoStreamer:
    """
    Handles streaming frames from YouTube videos using yt-dlp and OpenCV.
    """
    def __init__(self, youtube_url, sampling_rate=1.0):
        """
        :param youtube_url: The URL of the YouTube video.
        :param sampling_rate: Number of frames to extract per second.
        """
        self.youtube_url = youtube_url
        self.sampling_rate = sampling_rate
        self.stream_url = None
        self.video_info = None

    def _get_stream_url(self):
        """Extracts the direct stream URL from YouTube."""
        ydl_opts = {
            'format': 'bestvideo[height<=720]', # 720p for balance between detail and speed
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self.video_info = ydl.extract_info(self.youtube_url, download=False)
            self.stream_url = self.video_info['url']
        return self.stream_url

    def stream_frames(self, output_dir="data/frames"):
        """
        Streams and saves frames from the video.
        Yields (frame_data, timestamp) for each sampled frame.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self._get_stream_url()
        cap = cv2.VideoCapture(self.stream_url)

        if not cap.isOpened():
            raise Exception("Could not open video stream.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps / self.sampling_rate) if self.sampling_rate > 0 else 1
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                timestamp = frame_count / fps
                # Optional: Save frame to disk for verification/caching
                # frame_path = os.path.join(output_dir, f"frame_{frame_count}.jpg")
                # cv2.imwrite(frame_path, frame)
                yield frame, timestamp
            
            frame_count += 1

        cap.release()

if __name__ == "__main__":
    # Test with a sample video
    SAMPLE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Never gonna give you up
    streamer = VideoStreamer(SAMPLE_URL, sampling_rate=0.5) # 1 frame every 2 seconds
    print(f"Starting stream for: {SAMPLE_URL}")
    for i, (frame, ts) in enumerate(streamer.stream_frames()):
        print(f"Captured frame {i} at timestamp: {ts:.2f}s")
        if i >= 10: break # Stop after 10 frames for testing
