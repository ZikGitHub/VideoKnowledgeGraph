from youtube_transcript_api import YouTubeTranscriptApi
import re

class TranscriptFetcher:
    """
    Fetches and cleans transcripts from YouTube videos.
    """
    def __init__(self, youtube_url):
        self.youtube_url = youtube_url
        self.video_id = self._extract_video_id(youtube_url)

    def _extract_video_id(self, url):
        """Extracts the video ID from a YouTube URL."""
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        raise ValueError("Invalid YouTube URL")

    def get_transcript(self):
        """
        Fetches the transcript as a list of dictionaries with 'text', 'start', and 'duration'.
        """
        try:
            # Instantiate the API and use .fetch() as required by this version
            api = YouTubeTranscriptApi()
            transcript = api.fetch(self.video_id)
            return transcript
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return None

    def get_full_text(self):
        """Returns the entire transcript as a single string."""
        transcript = self.get_transcript()
        if transcript:
            return " ".join([item['text'] for item in transcript])
        return ""

if __name__ == "__main__":
    SAMPLE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Never gonna give you up
    fetcher = TranscriptFetcher(SAMPLE_URL)
    print(f"Fetching transcript for ID: {fetcher.video_id}")
    transcript = fetcher.get_transcript()
    if transcript:
        print(f"Extracted {len(transcript)} segments.")
        print(f"First 3 segments: {transcript[:3]}")
