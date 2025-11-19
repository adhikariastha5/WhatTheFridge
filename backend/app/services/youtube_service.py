from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse


class YouTubeService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_recipes(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube for recipe videos using web scraping"""
        try:
            search_query = f"{query} recipe cooking"
            # URL encode the search query
            encoded_query = urllib.parse.quote_plus(search_query)
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            # YouTube stores video data in script tags with JSON
            # Look for the initial data that contains video information
            scripts = soup.find_all('script')
            video_data_found = False
            
            for script in scripts:
                if script.string and 'var ytInitialData' in script.string:
                    # Extract JSON data
                    script_text = script.string
                    # Find the JSON object
                    start_idx = script_text.find('var ytInitialData = ')
                    if start_idx != -1:
                        start_idx += len('var ytInitialData = ')
                        # Find the end of the JSON object (simplified - find matching brace)
                        brace_count = 0
                        end_idx = start_idx
                        for i, char in enumerate(script_text[start_idx:], start_idx):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = i + 1
                                    break
                        
                        if end_idx > start_idx:
                            try:
                                import json
                                json_str = script_text[start_idx:end_idx]
                                data = json.loads(json_str)
                                # Navigate the complex YouTube data structure
                                contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                                
                                for section in contents:
                                    item_section = section.get('itemSectionRenderer', {}).get('contents', [])
                                    for item in item_section:
                                        video_renderer = item.get('videoRenderer', {})
                                        if video_renderer:
                                            video_id = video_renderer.get('videoId', '')
                                            title = video_renderer.get('title', {}).get('runs', [{}])[0].get('text', 'Unknown Recipe')
                                            thumbnail_data = video_renderer.get('thumbnail', {}).get('thumbnails', [])
                                            thumbnail = thumbnail_data[-1].get('url', '') if thumbnail_data else ''
                                            
                                            if video_id and len(videos) < max_results:
                                                videos.append({
                                                    'title': title,
                                                    'url': f"https://www.youtube.com/watch?v={video_id}",
                                                    'thumbnail': thumbnail,
                                                    'duration': '',
                                                    'video_id': video_id,
                                                    'source': 'youtube'
                                                })
                                                video_data_found = True
                                                
                                                if len(videos) >= max_results:
                                                    break
                                    
                                    if len(videos) >= max_results:
                                        break
                            except Exception as e:
                                print(f"Error parsing YouTube JSON: {str(e)}")
                                continue
            
            # Fallback: Simple regex search if JSON parsing fails
            if not video_data_found or len(videos) == 0:
                # Look for video links in the page
                video_links = soup.find_all('a', href=re.compile(r'/watch\?v='))
                seen_ids = set()
                
                for link in video_links[:max_results * 2]:  # Get more to filter
                    href = link.get('href', '')
                    if '/watch?v=' in href:
                        video_id = href.split('watch?v=')[1].split('&')[0]
                        if video_id not in seen_ids and len(videos) < max_results:
                            seen_ids.add(video_id)
                            title = link.get('title', 'Unknown Recipe') or 'Unknown Recipe'
                            videos.append({
                                'title': title,
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'thumbnail': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                                'duration': '',
                                'video_id': video_id,
                                'source': 'youtube'
                            })
            
            print(f"Found {len(videos)} YouTube videos for query: {query}")
            return videos
        except Exception as e:
            print(f"Error searching YouTube: {str(e)}")
            import traceback
            traceback.print_exc()
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

