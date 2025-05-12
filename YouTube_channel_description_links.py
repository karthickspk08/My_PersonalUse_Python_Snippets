import requests
import re

API_KEY = "Enter Your API Key"  # Replace with your API key
CHANNEL_ID = "enter channel id"  # Replace with the target channel's ID

def get_uploads_playlist_id(api_key, channel_id):
    """Retrieve the uploads playlist ID for the given channel ID."""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def get_all_video_ids(api_key, playlist_id):
    """Retrieve all video IDs from the uploads playlist."""
    video_ids = []
    next_page_token = None
    while True:
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={api_key}"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        video_ids.extend([item['contentDetails']['videoId'] for item in data.get('items', [])])
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    return video_ids

def extract_links(descriptions):
    """Extract links from descriptions using regex."""
#    pattern = re.compile(r'https?://(?:.*\.)?google\.com/\S+')
pattern = re.compile(r'https?://(?:.*\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/\S+')
    links = []
    for desc in descriptions:
        desc_clean = desc.replace('\n', ' ')
        found_links = pattern.findall(desc_clean)
        links.extend(found_links)
    return links

def main():
    try:
        # Get the uploads playlist ID
        playlist_id = get_uploads_playlist_id(API_KEY, CHANNEL_ID)
        print(f"Found uploads playlist ID: {playlist_id}")

        # Retrieve all video IDs
        video_ids = get_all_video_ids(API_KEY, playlist_id)
        print(f"Found {len(video_ids)} videos.")

        # Process videos in batches of 50
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            video_ids_str = ','.join(batch)
            url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_ids_str}&key={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extract descriptions and links
            descriptions = [item['snippet']['description'] for item in data.get('items', [])]
            links = extract_links(descriptions)

            # Append links to file
            if links:
                with open('links.txt', 'a') as f:
                    for link in links:
                        f.write(f"{link}\n")
                print(f"Added {len(links)} links from batch {i//50 + 1}")

        print("Done! Check links.txt for the collected links.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__"
      :
    main()
