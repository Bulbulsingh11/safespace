"""
scraper.py — Instagram Comment Scraper
Uses direct Instagram API requests with browser cookies (no instaloader).
This approach mimics a real browser and is much harder for Instagram to block.
"""
from __future__ import annotations

import re
import os
import json
import requests


# Instagram's web app ID (public, used by all Instagram web clients)
IG_APP_ID = "936619743392459"


def extract_shortcode(url: str) -> str:
    """Extract the shortcode from an Instagram post or reel URL."""
    patterns = [
        r"instagram\.com/p/([A-Za-z0-9_-]+)",
        r"instagram\.com/reel/([A-Za-z0-9_-]+)",
        r"instagram\.com/tv/([A-Za-z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid Instagram URL. Please provide a valid post or reel link.")


def shortcode_to_media_id(shortcode: str) -> str:
    """Convert Instagram shortcode to numeric media ID (no API call needed)."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    media_id = 0
    for char in shortcode:
        media_id = media_id * 64 + alphabet.index(char)
    return str(media_id)


def _build_session_from_cookies_file(cookies_file_path: str) -> requests.Session:
    """
    Parse a Netscape cookies.txt file and build a requests Session
    with all Instagram cookies loaded and proper browser headers set.
    """
    session = requests.Session()
    ig_cookies = {}

    with open(cookies_file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            domain, _, path, _, _, name, value = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
            if "instagram.com" in domain:
                session.cookies.set(name, value, domain=".instagram.com", path="/")
                ig_cookies[name] = value

    if not ig_cookies:
        raise RuntimeError(
            "No Instagram cookies found in the uploaded file. "
            "Make sure you export cookies from instagram.com while logged in."
        )

    missing = [k for k in ["sessionid", "csrftoken"] if k not in ig_cookies]
    if missing:
        raise RuntimeError(
            f"Cookies file is missing required cookies: {missing}. "
            "Please log into Instagram first, then export cookies."
        )

    csrf = ig_cookies.get("csrftoken", "")
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-IG-App-ID": IG_APP_ID,
        "X-ASBD-ID": "198387",
        "X-CSRFToken": csrf,
        "Referer": "https://www.instagram.com/",
        "Origin": "https://www.instagram.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
    })
    return session


def _fetch_comments_via_api(
    session: requests.Session,
    media_id: str,
    max_comments: int,
) -> list[dict]:
    """
    Fetch comments from Instagram's internal API endpoint.
    """
    comments = []
    url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
    params = {
        "can_support_threading": "true",
        "permalink_enabled": "false",
    }

    while len(comments) < max_comments:
        resp = session.get(url, params=params, timeout=15)

        if resp.status_code == 401:
            raise RuntimeError(
                "Instagram returned 401 Unauthorized. Your cookies may have expired — "
                "please re-export a fresh cookies.txt from Instagram and try again."
            )
        if resp.status_code == 403:
            raise RuntimeError(
                "Instagram returned 403 Forbidden. Your account may be rate-limited. "
                "Try again in a few minutes or use Manual Entry mode."
            )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Instagram API returned status {resp.status_code}. "
                "Try again or use Manual Entry mode."
            )

        try:
            data = resp.json()
        except Exception:
            raise RuntimeError(
                "Instagram returned an unexpected response (possibly a login redirect). "
                "Your cookies may be invalid — re-export and try again."
            )

        for item in data.get("comments", []):
            text = item.get("text", "").strip()
            user = item.get("user", {}).get("username", "unknown")
            if text:
                comments.append({"username": user, "comment": text})
            if len(comments) >= max_comments:
                break

        # Pagination
        next_min_id = data.get("next_min_id")
        if not next_min_id or not data.get("has_more_comments"):
            break
        params["min_id"] = next_min_id

    return comments


def scrape_comments(
    url: str,
    max_comments: int = 50,
    browser: str = "firefox",
    ig_username: str = "",
    ig_password: str = "",
    cookies_file_path: str = "",
) -> list[dict]:
    """
    Scrape comments from an Instagram post using direct API requests.
    Requires a valid cookies.txt file exported from your browser.
    """
    shortcode = extract_shortcode(url)
    media_id = shortcode_to_media_id(shortcode)

    if cookies_file_path and os.path.exists(cookies_file_path):
        session = _build_session_from_cookies_file(cookies_file_path)
    elif ig_username and ig_password:
        # Try username/password via instaloader as last resort
        try:
            import instaloader
            loader = instaloader.Instaloader(quiet=True, download_comments=True)
            loader.login(ig_username, ig_password)
            # Use instaloader's session
            session = loader.context._session
            session.headers.update({
                "X-IG-App-ID": IG_APP_ID,
                "Referer": "https://www.instagram.com/",
            })
        except Exception as e:
            raise RuntimeError(f"Login failed: {e}")
    else:
        raise RuntimeError(
            "No authentication provided. Please upload a cookies.txt file "
            "or use the 'Use Password Instead' option."
        )

    comments = _fetch_comments_via_api(session, media_id, max_comments)

    if not comments:
        raise RuntimeError(
            "No comments found. The post may have comments disabled, "
            "or the post URL might be wrong."
        )

    return comments


# ---------------------------------------------------------------------------
# Demo / fallback data
# ---------------------------------------------------------------------------
DEMO_COMMENTS = [
    {"username": "user_alpha",       "comment": "Love this photo! Great work 🔥"},
    {"username": "toxic_troll99",    "comment": "You're the worst, nobody likes you, go disappear"},
    {"username": "sunshine_vibes",   "comment": "This is so inspiring, keep going!"},
    {"username": "hater_2025",       "comment": "Ugly and stupid, you should be ashamed of yourself"},
    {"username": "photo_fan",        "comment": "Amazing composition and colors!"},
    {"username": "keyboard_warrior", "comment": "You're a disgusting piece of trash, die already"},
    {"username": "nature_lover",     "comment": "Beautiful scenery, where was this taken?"},
    {"username": "bully_master",     "comment": "Kill yourself you worthless idiot, nobody will care"},
    {"username": "art_critic",       "comment": "Interesting perspective, I like the framing"},
    {"username": "mean_commenter",   "comment": "You look terrible, stop posting your ugly face"},
    {"username": "positive_pete",    "comment": "Sending love and good vibes!"},
    {"username": "dark_humor_guy",   "comment": "Imagine being this cringe in 2025 lmao"},
    {"username": "genuine_fan",      "comment": "You always post such quality content"},
    {"username": "rage_account",     "comment": "Shut up you pathetic loser, everyone hates you"},
    {"username": "travel_buddy",     "comment": "Adding this to my bucket list!"},
    {"username": "shade_thrower",    "comment": "Desperate for attention much?"},
    {"username": "supportive_sam",   "comment": "Don't listen to the haters, you're awesome!"},
    {"username": "vile_commenter",   "comment": "You deserve to suffer, absolute waste of space"},
    {"username": "casual_viewer",    "comment": "Nice post"},
    {"username": "cyber_bully_01",   "comment": "Go die in a hole you stupid worthless scum"},
]
