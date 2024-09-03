import requests
from bs4 import BeautifulSoup
import os
import argparse
from urllib.parse import urljoin, unquote
from tqdm import tqdm
import concurrent.futures
import signal
import sys

# Default values (modify these as needed)
DEFAULT_START_URL = "https://archive.org/download/The_Gray_Bearded_Green_Beret_Archive/The%20Gray%20Bearded%20Green%20Beret/"
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Downloads/archive_org_videos")

# Global flag to signal the script to stop
stop_script = False

def signal_handler(sig, frame):
    global stop_script
    print("\nStopping the script gracefully...")
    stop_script = True

def get_links(url):
    print(f"Fetching links from: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        directory_listing = soup.find(class_="download-directory-listing")
        
        if directory_listing:
            links = [urljoin(url, a['href']) for a in directory_listing.find_all('a', href=True)]
            print(f"Found {len(links)} links in the download directory listing")
        else:
            print("Could not find the download directory listing")
            links = []
        
        return links
    except requests.RequestException as e:
        print(f"Error fetching links from {url}: {e}")
        return []

def get_video_link(page_url):
    if stop_script:
        return None
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            if link['href'].lower().endswith(('.mp4', '.mkv')):
                return urljoin(page_url, link['href'])
        
        return None
    except requests.RequestException as e:
        print(f"Error fetching video link from {page_url}: {e}")
        return None

def download_file(url, output_dir):
    if stop_script:
        return None
    filename = unquote(url.split('/')[-1]).replace('%20', ' ')
    local_filename = os.path.join(output_dir, filename)
    
    if os.path.exists(local_filename):
        print(f"{filename} already exists. Skipping download.")
        return local_filename
    
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(local_filename, 'wb') as f, tqdm(
                desc=filename,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            ) as progress_bar:
                for data in r.iter_content(chunk_size=8192):
                    if stop_script:
                        f.close()
                        os.remove(local_filename)
                        return None
                    size = f.write(data)
                    progress_bar.update(size)
        
        return local_filename
    except requests.RequestException as e:
        print(f"Error downloading {filename}: {e}")
        if os.path.exists(local_filename):
            os.remove(local_filename)
        return None

def main(start_url, output_dir):
    print(f"Starting script with URL: {start_url}")
    print(f"Output directory: {output_dir}")
    print("Press Ctrl+C at any time to stop the script")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        print("Fetching initial links")
        initial_links = get_links(start_url)
        
        if stop_script:
            return
        
        print("Extracting video links from each page")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            video_links = list(filter(None, executor.map(get_video_link, initial_links)))
        
        print(f"Found {len(video_links)} video links")
        
        if video_links and not stop_script:
            print("Starting downloads")
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                list(executor.map(lambda url: download_file(url, output_dir), video_links))
            print("All downloads completed")
        else:
            print("No video links found or script stopped.")
        
    except Exception as e:
        print(f"Unexpected error in main function: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download videos from archive.org")
    parser.add_argument("-u", "--url", help="The starting URL of the archive.org directory", default=DEFAULT_START_URL)
    parser.add_argument("-o", "--output_dir", help="The directory to save the downloaded videos", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Script started")
    main(args.url, args.output_dir)
    print("Script finished")
