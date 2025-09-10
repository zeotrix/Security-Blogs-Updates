# rss_monitor_telegram.py

import feedparser
import json
import os
import requests
import time
import xml.etree.ElementTree as ET

# This script checks a list of RSS feeds from an OPML file hosted online
# for new posts and sends them to a Telegram channel.

# --- Configuration ---
OPML_URL = "https://github.com/zeotrix/Security_Materials/raw/main/feedly-2022-06-10.opml"
LAST_POSTS_FILE = "last_posts.json"

# Retrieve Telegram credentials from environment variables for security.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def load_rss_feeds_from_opml(opml_url):
    """
    Downloads and parses an OPML file from a URL to extract RSS feed URLs.
    """
    print(f"Downloading OPML file from {opml_url}...")
    try:
        response = requests.get(opml_url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading OPML file: {e}")
        return []

    feeds = []
    try:
        # Use .fromstring() to parse the XML content from the response
        root = ET.fromstring(response.content)

        # Find all <outline> elements that have the 'xmlUrl' attribute
        for outline in root.findall(".//outline[@xmlUrl]"):
            feed_url = outline.get('xmlUrl')
            if feed_url:
                feeds.append(feed_url)
    except ET.ParseError as e:
        print(f"Error parsing OPML content: {e}")
        return []

    print(f"Found {len(feeds)} RSS feeds in the OPML file.")
    return feeds

def load_last_posts(filename):
    """
    Loads the dictionary of last seen post titles from a JSON file.
    If the file does not exist, an empty dictionary is returned.
    """
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: '{filename}' is corrupted. Starting with an empty state.")
            return {}
    return {}

def save_last_posts(filename, last_posts):
    """
    Saves the dictionary of last seen post titles to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(last_posts, f, indent=4)

def check_for_new_posts(feed_url, last_posts):
    """
    Parses a single RSS feed and returns a list of new posts since the last check.
    """
    try:
        feed = feedparser.parse(feed_url)
        feed_id = feed.feed.title if hasattr(feed.feed, 'title') else feed_url
        last_seen_title = last_posts.get(feed_id)
        
        new_posts = []
        
        for entry in reversed(feed.entries):
            title = entry.title if hasattr(entry, 'title') else "Untitled"
            link = entry.link if hasattr(entry, 'link') else "No Link"
            
            if title == last_seen_title:
                break
                
            new_posts.append({'title': title, 'link': link})
            
        if feed.entries:
            last_posts[feed_id] = feed.entries[0].title
            
        return new_posts
        
    except Exception as e:
        print(f"Error checking feed {feed_url}: {e}")
        return []

def send_telegram_message(message):
    """
    Sends a message to a Telegram channel using the Bot API.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("Error: Telegram bot token or channel ID not set.")
        print("Please set the TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID environment variables.")
        return

    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': 'true' # Prevents Telegram from creating a link preview
    }
    
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload)
        response.raise_for_status()
        print("Message successfully sent to Telegram.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")

def main():
    """
    Main function to run the RSS monitor once.
    """
    print("Starting RSS Feed Monitor...")
    
    rss_urls = load_rss_feeds_from_opml(OPML_URL)
    if not rss_urls:
        return
        
    last_posts = load_last_posts(LAST_POSTS_FILE)

    new_posts_found = False
    for url in rss_urls:
        new_posts = check_for_new_posts(url, last_posts)
        
        if new_posts:
            new_posts_found = True
            
            message = f"**New Posts from {url}**\n\n"
            for post in new_posts:
                message += f"**{post['title']}**\n"
                message += f"Link: {post['link']}\n\n"
            
            send_telegram_message(message)
            time.sleep(1) # Small delay to avoid hitting Telegram's rate limits
        else:
            send_telegram_message(f"**No Found Posts from {url}**\n\n")
            time.sleep(1) 

    if not new_posts_found:
        print("No new posts found for any feed.")

    save_last_posts(LAST_POSTS_FILE, last_posts)
    print("\nProcess complete.")
    send_telegram_message("No more posts for today!")

if __name__ == "__main__":
    main()
