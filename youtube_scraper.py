"""
youtube_scraper.py — YouTube Comment Fetcher
Uses the free YouTube Data API v3 (no login required).
Get a free API key at: https://console.cloud.google.com/ → APIs → YouTube Data API v3
"""
from __future__ import annotations

import re
import requests


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r"youtube\.com/watch\?v=([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL. Please paste a full YouTube video link.")


def fetch_youtube_comments(
    url: str,
    api_key: str,
    max_comments: int = 50,
) -> list[dict]:
    """
    Fetch up to max_comments comments from a YouTube video.

    Parameters
    ----------
    url : str
        Full YouTube video URL.
    api_key : str
        YouTube Data API v3 key (free from Google Cloud Console).
    max_comments : int
        Maximum number of comments to fetch.

    Returns
    -------
    list[dict]
        Each dict has keys: "username", "comment".
    """
    if not api_key or not api_key.strip():
        raise ValueError(
            "YouTube API key is required. "
            "Get a free key at https://console.cloud.google.com/ → "
            "Enable APIs → YouTube Data API v3 → Credentials → Create API Key."
        )

    video_id = extract_video_id(url)
    comments = []
    page_token = None

    while len(comments) < max_comments:
        params = {
            "part": "snippet",
            "videoId": video_id,
            "key": api_key.strip(),
            "maxResults": min(100, max_comments - len(comments)),
            "textFormat": "plainText",
            "order": "relevance",
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/commentThreads",
            params=params,
            timeout=15,
        )

        if resp.status_code == 400:
            raise RuntimeError(
                "Invalid API key or video ID. "
                "Make sure you copied the API key correctly."
            )
        if resp.status_code == 403:
            data = resp.json()
            reason = data.get("error", {}).get("errors", [{}])[0].get("reason", "")
            if reason == "commentsDisabled":
                raise RuntimeError("Comments are disabled on this video.")
            raise RuntimeError(
                "API quota exceeded or key restricted. "
                "Check your Google Cloud Console quota."
            )
        if resp.status_code != 200:
            raise RuntimeError(f"YouTube API error: HTTP {resp.status_code}")

        data = resp.json()

        for item in data.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "username": snippet.get("authorDisplayName", "unknown").lstrip("@"),
                "comment": snippet.get("textDisplay", "").strip(),
            })
            if len(comments) >= max_comments:
                break

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    if not comments:
        raise RuntimeError("No comments found on this video.")

    return comments
