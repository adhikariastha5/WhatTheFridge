from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional
import re


class YouTubeService:
    def __init__(self):
        pass

    def search_recipes(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube for recipe videos"""
        try:
            search_query = f"{query} recipe cooking"
            videos_search = VideosSearch(search_query, limit=max_results)
            results = videos_search.result()
            
            videos = []
            for result in results.get('result', []):
                video_id = result.get('id')
                if video_id:
                    videos.append({
                        'title': result.get('title', ''),
                        'url': result.get('link', f"https://www.youtube.com/watch?v={video_id}"),
                        'thumbnail': result.get('thumbnails', [{}])[0].get('url', '') if result.get('thumbnails') else '',
                        'duration': result.get('duration', ''),
                        'video_id': video_id,
                        'source': 'youtube'
                    })
            return videos
        except Exception as e:
            print(f"Error searching YouTube: {str(e)}")
            return []

    def get_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript from YouTube video"""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([item['text'] for item in transcript_list])
            return transcript_text
        except Exception as e:
            print(f"Error getting transcript: {str(e)}")
            # Try to get transcript in different languages
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for transcript in transcript_list:
                    try:
                        fetched = transcript.fetch()
                        transcript_text = ' '.join([item['text'] for item in fetched])
                        return transcript_text
                    except:
                        continue
            except:
                pass
            return None

    def extract_steps_from_transcript(self, transcript: str) -> List[str]:
        """Extract cooking steps from transcript text"""
        # Simple heuristic: look for numbered steps or time markers
        steps = []
        lines = transcript.split('.')
        
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Filter out very short fragments
                # Look for step indicators
                if any(keyword in line.lower() for keyword in ['step', 'first', 'next', 'then', 'now', 'add', 'mix', 'cook', 'heat']):
                    steps.append(line)
        
        return steps[:20]  # Limit to 20 steps

