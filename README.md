# archive.org_fileripper
Rips all files (by default .mp4 and .mkv videos) from ```achive.org/download/*``` pages through the commandline. No browser needed.

## Use Case
Archive.org already provides a way to download multiple files by having them sent to a .zip file first.

However, in the case of collections that are too large (over 50GB) this option is not available and will fail due to filesize. It is also extremely slow to generate the .zip even if does work.

Furthermore, if a page also hads hundreds or thousands of files and you only want to download eg. videos, even if it works you will get a .zip with mixed contents and additional size.

Even if the .zip is created, Archive.org limits the download speed to between 500KB/s and 1.2MB/s per file. If your .zip is several gigabytes this can take a long time (hours or days) to download and will likely fail.

So I created this script. It will download whatever file extensions you choose (by default .mp4 & .mkv) on an archive.org page. It will download between 4 and 5 files at a time (the maximum allowed by archive.org) and at the fastest possible speed through the command line. It uses python3 and a few basic libraries. The current progress is displayed whilst the script is running including:

* Filename of file being downloaded
* Current speed
* Current downloading time
* Estimated remaining time

There is also basic verbose error logging.

## Usage
1. Simply specify the ```DEFAULT_START_URL``` of the page with all of the links for that archive.org page. 
For example: ```https://archive.org/download/<your_page_of_links_here>```

2. Also specify the ```DEFAULT_OUTPUT_DIR``` eg. ```~/Downloads/archive_org_videos```

3. Run the script.

The script requires:

* Python3
* Pip
* BeautifulSoup
* urljoin
* unquote
* tqdm

The script will fetch the files (currently .mp4 and .mkv) files from any of the links within the ```'download-directory-listing'``` class on the page.

![fileripperdownload](https://i.postimg.cc/0jpLC8kx/image.png)

![image](https://github.com/user-attachments/assets/6b2f1e72-6abe-4bf4-9862-2ed162dee51c)


You can also change the file extensions you are interested in downloading, on line 62 (by default .mp4 and .mkv files)
```if link['href'].lower().endswith(('.mp4', '.mkv')):```

Quit the script gacefully with "Q+ENTER" keyboard input.

## Troubleshooting
If in the future this script breaks.

1. Check if your links are still within the above class.
2. Be sure that you are on the right page. This script is configured to only work on old HTML directory structure pages that contain a list of bare links to pages with direct links to files. eg. ```https://archive.org/download/<your_page_of_links_here>/<list_of_actual_files_here>```
3. Start at the top page, which contains all the links to other pages which have the files. The script does not indefinitely follow links to try and find matching video files.
4. Ensure the page actually has a file with a matching file extension on it.
5. Open an Issue Report on Github

Absolutely no warranty is implied using this script.

Do not use this script to break Archive.org's ToS.
