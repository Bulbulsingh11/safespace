"""
whatsapp_parser.py — WhatsApp Chat Export Parser
Parses the .txt file exported from WhatsApp (Android & iOS formats).

How to export from WhatsApp:
  Android: Open chat → ⋮ → More → Export chat → Without media
  iPhone:  Open chat → Contact name → Export Chat → Without media
"""

import re
from typing import List, Dict


# WhatsApp export patterns
# Android: "07/03/2026, 11:32 pm - Username: message"
# iOS:     "[07/03/2026, 11:32:45 PM] Username: message"
PATTERNS = [
    # Android format
    re.compile(
        r"^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)\s*-\s*([^:]+):\s*(.+)$"
    ),
    # iOS format
    re.compile(
        r"^\[\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}:\d{2}\s*(?:am|pm|AM|PM)\]\s*([^:]+):\s*(.+)$"
    ),
    # 24-hour Android: "07/03/2026, 23:32 - Username: message"
    re.compile(
        r"^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*-\s*([^:]+):\s*(.+)$"
    ),
    # 24-hour iOS: "[07/03/2026, 23:32:45] Username: message"
    re.compile(
        r"^\[\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}:\d{2}\]\s*([^:]+):\s*(.+)$"
    ),
]

# System messages to skip
SKIP_PHRASES = [
    "messages and calls are end-to-end encrypted",
    "changed the subject",
    "added you",
    "left",
    "created group",
    "changed this group",
    "changed their phone number",
    "you were added",
    "security code changed",
    "<media omitted>",
    "null",
    "missed voice call",
    "missed video call",
    "this message was deleted",
]


def parse_whatsapp_chat(text: str, max_messages: int = 100) -> List[Dict]:
    """
    Parse WhatsApp chat export text into a list of {username, comment} dicts.

    Parameters
    ----------
    text : str
        Raw content of the WhatsApp .txt export file.
    max_messages : int
        Maximum number of messages to return.

    Returns
    -------
    list[dict]
        Each dict has keys: "username", "comment".
    """
    messages = []
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        matched = False
        for pattern in PATTERNS:
            m = pattern.match(line)
            if m:
                username = m.group(1).strip()
                message = m.group(2).strip()
                matched = True

                # Skip system messages
                msg_lower = message.lower()
                if any(skip in msg_lower for skip in SKIP_PHRASES):
                    break

                # Skip very short/empty messages
                if len(message) < 2:
                    break

                messages.append({
                    "username": username,
                    "comment": message,
                })
                break

        if len(messages) >= max_messages:
            break

    return messages


def parse_whatsapp_file(file_bytes: bytes, max_messages: int = 100) -> List[Dict]:
    """
    Parse a WhatsApp chat export from raw file bytes.
    Tries UTF-8 first, then falls back to latin-1.
    """
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")

    messages = parse_whatsapp_chat(text, max_messages)

    if not messages:
        raise ValueError(
            "No WhatsApp messages found in this file. "
            "Make sure you exported a chat from WhatsApp (File → Export Chat → Without Media). "
            "The file should contain lines like: '07/03/2026, 11:32 pm - Name: message'"
        )

    return messages
