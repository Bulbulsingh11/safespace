"""
test_scraper.py — Run this to diagnose Instagram scraping issues.
Usage: py -3.12 test_scraper.py <cookies.txt path> <instagram post url>
Example: py -3.12 test_scraper.py cookies.txt https://www.instagram.com/reel/ABC123/
"""

import sys
import os

def test(cookies_path, post_url):
    import requests
    import re

    # --- Step 1: Parse cookies ---
    print(f"\n[1] Reading cookies from: {cookies_path}")
    session = requests.Session()
    ig_cookies = {}
    with open(cookies_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 7 and "instagram.com" in parts[0]:
                name, value = parts[5], parts[6]
                session.cookies.set(name, value, domain=".instagram.com", path="/")
                ig_cookies[name] = value

    print(f"    Found {len(ig_cookies)} Instagram cookies")
    for key in ["sessionid", "csrftoken", "ds_user_id", "mid"]:
        status = "✓" if key in ig_cookies else "✗ MISSING"
        print(f"    {key}: {status}")

    if "sessionid" not in ig_cookies:
        print("\n❌ ERROR: sessionid cookie not found. Export cookies while logged into Instagram.")
        return

    # --- Step 2: Convert shortcode to media ID ---
    patterns = [r"instagram\.com/p/([A-Za-z0-9_-]+)", r"instagram\.com/reel/([A-Za-z0-9_-]+)"]
    shortcode = None
    for p in patterns:
        m = re.search(p, post_url)
        if m:
            shortcode = m.group(1)
            break
    if not shortcode:
        print("❌ Could not extract shortcode from URL")
        return

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    media_id = 0
    for c in shortcode:
        media_id = media_id * 64 + alphabet.index(c)
    print(f"\n[2] Shortcode: {shortcode} → Media ID: {media_id}")

    # --- Step 3: Call Instagram API ---
    csrf = ig_cookies.get("csrftoken", "")
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "X-CSRFToken": csrf,
        "Referer": "https://www.instagram.com/",
        "Accept": "*/*",
    })

    api_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
    print(f"\n[3] Calling: {api_url}")
    try:
        resp = session.get(api_url, params={"can_support_threading": "true"}, timeout=15)
        print(f"    HTTP Status: {resp.status_code}")
        print(f"    Response (first 500 chars):\n{resp.text[:500]}")
        if resp.status_code == 200:
            data = resp.json()
            comments = data.get("comments", [])
            print(f"\n✅ SUCCESS! Got {len(comments)} comments")
            for c in comments[:3]:
                print(f"   @{c.get('user',{}).get('username','?')}: {c.get('text','')[:60]}")
        else:
            print(f"\n❌ API call failed with status {resp.status_code}")
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: py -3.12 test_scraper.py <cookies.txt> <instagram_url>")
        print("Example: py -3.12 test_scraper.py cookies.txt https://www.instagram.com/reel/DSzxXM5kcRR/")
    else:
        test(sys.argv[1], sys.argv[2])
