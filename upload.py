import os
import sys
import re
import requests
import subprocess
import random
import json
import base64
import ffmpeg
from pathlib import Path
from pymediainfo import MediaInfo
from torf import Torrent
from tqdm import tqdm


def print_banner():
    banner = (
        "\n"
        "\033[97m     ░██████╗██████╗░░█████╗░██████╗░████████╗░██████╗  ░█████╗░██╗░░░██╗██╗░░░░░████████╗\n"
        '\033[97m     ██╔════╝██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔════╝  ██╔══██╗██║░░░██║██║░░░░░╚══██╔══╝\033[38;5;208m       _.-=""=-._	\n'
        "\033[97m     ╚█████╗░██████╔╝██║░░██║██████╔╝░░░██║░░░╚█████╗░  ██║░░╚═╝██║░░░██║██║░░░░░░░░██║░░░\033[38;5;208m     .'\\\\-++++-//'.\n"
        "\033[97m     ░╚═══██╗██╔═══╝░██║░░██║██╔══██╗░░░██║░░░░╚═══██╗  ██║░░██╗██║░░░██║██║░░░░░░░░██║░░░\033[38;5;208m    (  ||      ||  )\n"
        "\033[97m     ██████╔╝██║░░░░░╚█████╔╝██║░░██║░░░██║░░░██████╔╝  ╚█████╔╝╚██████╔╝███████╗░░░██║░░░\033[38;5;208m     './/      \\\\.'\n"
        "\033[97m     ╚═════╝░╚═╝░░░░░░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░  ░╚════╝░░╚═════╝░╚══════╝░░░╚═╝░░░\033[38;5;208m       `'-=..=-'`\n"
        "\033[38;5;196m                                                                                  UPLOADER\033[0m\n"
    )
    print(banner)


def print_help():
    help_text = """
Sports Cult Uploader v0.1

Usage: python upload.py [options] -c <category_name> <video_file_or_directory>

Arguments:
  -c <category_name>        Required. The name of the category to upload the video to. (e.g., UFC, "American Football")
  <video_file_or_directory> The video file or directory containing video files (e.g., video.mp4 or /path/to/tvseason)

Options:
  --anonymous, -a           Flag to upload the video anonymously.
  --show-categories, -s     Lists available categories and exits.
  --yes, -y                 Proceed with upload without asking for confirmation.  
  --help, -h                Show this help message and exit.

Description:
  This script processes video files for upload to Sportscult. It generates a .torrent file, takes screenshots,
  retrieves video metadata, and uploads the video to Sportscult with a set of thumbnail images. You need to provide
  a valid 'sportscult.conf' configuration file with necessary details like cookie, PID, and imgbb API key.

Example:
  python upload.py -c UFC /path/to/videos --anonymous
  python upload.py -c "American Football" video.mp4
  python upload.py -c NBA /path/to/videos --yes  
"""
    print(help_text)
    sys.exit(0)


def show_categories(categories):
    print("Available Categories:")
    for category_id, category_name in categories.items():
        print(f"- {category_name}")
    sys.exit(0)


def read_sportscult_config():
    config_path = Path(__file__).parent / "sportscult.conf"
    if not config_path.exists():
        print("Configuration file 'sportscult.conf' not found.")
        sys.exit(1)

    config = {}
    with open(config_path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key.strip()] = value.strip()
    return config


def read_categories():
    categories_path = Path(__file__).parent / "categories.json"
    if not categories_path.exists():
        print("Categories file 'categories.json' not found.")
        sys.exit(1)

    with open(categories_path, "r") as f:
        categories = json.load(f)
    return categories


def get_category_id(categories, category_name):
    for category_id, category_name_value in categories.items():
        if category_name_value.lower() == category_name.lower():
            return category_id
    print(f"Category '{category_name}' not found.")
    sys.exit(1)


def create_meta_dir(base_name):
    script_dir = Path(__file__).parent
    meta_dir = script_dir / "temp" / base_name
    meta_dir.mkdir(parents=True, exist_ok=True)
    print(f"Metadata folder created: {meta_dir}")
    return meta_dir

from pymediainfo import MediaInfo
import re
from pathlib import Path

def generate_mediainfo(video_file, meta_dir, isdir):
    try:
        media_info = MediaInfo.parse(video_file, output="STRING", full=False, mediainfo_options={'inform_version': '1'})
        
        media_info = re.sub(
            r"(Complete name\s+:)\s?.+", r"\1 {0}".format(video_file.name), media_info
        )

        if isdir:
            nfo_name = video_file.parent.name
        else:
            nfo_name = video_file.stem

        nfo_file = Path(meta_dir) / f"{nfo_name}.nfo"

        with open(nfo_file, "w", encoding="utf-8", newline="") as file:
            file.write(media_info)

        print(f"Mediainfo saved to: {nfo_file.name}")
        return nfo_file

    except Exception as e:
        print(f"Error generating media info: {e}")
        raise


def take_screenshots(video_file, meta_dir, isdir):
    if isdir:
        screenshot_name = video_file.parent.name
    else:
        screenshot_name = video_file.stem

    timestamps = [random.randint(0, 1200) for _ in range(4)] # Random timestamps within the first 20 minutes (1200 seconds)
    screenshot_paths = []

    with tqdm(
        total=len(timestamps),
        desc="Taking screenshots",
        unit="image",
        colour="#f16122",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} ",
        dynamic_ncols=True,
    ) as pbar:
        for i, timestamp in enumerate(timestamps):
            screenshot_path = meta_dir / f"{screenshot_name}_screenshot_{i+1:02d}.jpg"

            try:
                (
                    ffmpeg
                    .input(str(video_file), ss=timestamp)
                    .output(str(screenshot_path), vframes=1, q=2, loglevel="quiet")
                    .overwrite_output()
                    .run(quiet=True)
                )
                screenshot_paths.append(screenshot_path)
            except ffmpeg.Error as e:
                print(f"Error taking screenshot at {timestamp} seconds: {e}")
                sys.exit(1)

            pbar.update(1)

    return screenshot_paths

def upload_screenshots(screenshot_paths, imgbb_api_key):
    upload_url = "https://api.imgbb.com/1/upload"
    embedding_links = []

    with tqdm(
        total=len(screenshot_paths),
        desc="Uploading screenshots",
        unit="image",
        colour="#f16122",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
    ) as pbar:
        for screenshot in screenshot_paths:
            with open(screenshot, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            payload = {
                "key": imgbb_api_key,
                "image": base64_image,
            }

            response = requests.post(upload_url, data=payload)
            if response.status_code == 200:
                result = response.json()
                if result["status"] == 200:
                    viewer_url = result["data"]["url_viewer"]
                    image_url = result["data"]["url"]
                    thumbnail_linked = f"[url={viewer_url}][img]{image_url}[/img][/url]"
                    embedding_links.append(thumbnail_linked)
                else:
                    print(f"Error uploading image: {result}")
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")

            pbar.update(1)

    return embedding_links


def save_embedding_links(embedding_codes, video_file, meta_dir, isdir):
    if isdir:
        thumb_name = video_file.parent.name
    else:
        thumb_name = video_file.stem
        
    thumb_file_path = meta_dir / f"{thumb_name}.thumb"
    with open(thumb_file_path, "w", encoding="utf-8") as thumb_file:
        for code in embedding_codes:
            thumb_file.write(f"{code}")
    print(f"Embedding codes saved to: {thumb_file_path.name}")
    return thumb_file_path


def generate_torrent(video_file, meta_dir, pid, isdir):

    if isdir:
        torrent_name = video_file.parent.name
        target = video_file.parent
    else:
        torrent_name = video_file.stem
        target = video_file
            
    torrent_path = meta_dir / f"{torrent_name}.torrent"

    if torrent_path.exists():
        torrent_path.unlink()

    torrent = Torrent(
        path=str(target),
        trackers=[f"https://sportscult-announce.org/announce.php?pid={pid}"],
        private=True,
	    creation_date=None,
	    created_by='Sports Cult Uploader'
    )
    torrent.generate()
    torrent.write(str(torrent_path))

    print(f"Torrent generated: {torrent_path.name}")
    return torrent_path


def upload_to_sports_cult(video_file, nfo_file, cookie, user_agent, thumb_file_path, category_id, meta_dir, anonymous, torrent_path, isdir):
    
    config = read_sportscult_config()
    qb_address = config.get("qb_address", "http://localhost")
    qb_port = config.get("qb_port", "8080")
    qb_user = config.get("qb_user", "admin")
    qb_password = config.get("qb_password", "adminadmin")
    qbit_category = config.get("qbit_category", "default")

    with open(thumb_file_path, "r", encoding="utf-8") as thumb_file:
        thumb_content = thumb_file.read()

    with open(nfo_file, "r", encoding="utf-8") as nfo:
        nfo_content = nfo.read()

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "cookie": cookie,
        "referer": "https://sportscult.org/index.php?page=upload",
        "user-agent": user_agent,
    }

    files = {
        "torrent": (
            torrent_path.stem,
            open(str(torrent_path), "rb"),
            "application/x-bittorrent",
        ),
        "userfile": ("", "", "application/octet-stream"), 
    }

    data = {
        "user_id": None,
        "category": category_id,  # SportsCult category ID
        "filename": torrent_path.stem,
        "fontchange": None,
        "anonymous": anonymous,        
        "info": f"{thumb_content}\n[code]{nfo_content}[/code][url=https://github.com/costaht/sportscult-uploader][color=red]Uploaded with Sports Cult Uploader[/color][/url]",
    }

    # Make the upload request to SportsCult
    response = requests.post(
        "https://sportscult.org/index.php?page=upload",
        headers=headers,
        files=files,
        data=data,
    )
    
    if response.status_code == 200 and "Upload successful" in response.text:
        print("\033[92mUpload to Sports Cult 🏈 successful!\033[0m")

        if isdir:
            savepath = video_file.parent.parent.resolve()
        else:
            savepath = video_file.parent.resolve()

        qb_url = f"{qb_address}:{qb_port}/api/v2/torrents/add"
        qb_session = requests.Session()
        qb_session.post(
            f"{qb_address}:{qb_port}/api/v2/auth/login",
            data={"username": qb_user, "password": qb_password},
        )

        with open(torrent_path, "rb") as torrent_file:
            response = qb_session.post(
                qb_url,
                files={"torrents": torrent_file},
                data={
                    "category": qbit_category,
                    "skip_checking": "true",
                    "savepath": savepath,
                },
            )

        if response.status_code == 200:
            print("\033[92mTorrent successfully added to qBittorrent. \033[93mHappy Seeding! 🚀\033[0m")
        else:
            print(
                f"\033[91mFailed to add torrent to qBittorrent. Response: {response.text}\033[0m"
            )
    else:
        print(
            f"\033[91mUpload failed or unsuccessful. HTTP status code: {response.status_code}, response: {response.text}\033[0m"
        )


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_help()

    if "--show-categories" in args or "-s" in args:
        categories = read_categories()
        show_categories(categories)

    if "-c" not in args:
        print("Error: -c <category_name> is required.")
        print_help()

    category_name = args[args.index("-c") + 1]
    video_file_or_directory = args[-1]

    anonymous = "--anonymous" in args or "-a" in args
    auto_confirm = "--yes" in args or "-y" in args
    
    categories = read_categories()
    category_id = get_category_id(categories, category_name)
    path = Path(video_file_or_directory)
    config = read_sportscult_config()
    cookie = config.get("cookie")
    user_agent = config.get("user_agent")
    pid = config.get("pid")
    imgbb_api_key = config.get("imgbb_api_key")

    if not cookie or not pid or not imgbb_api_key:
        print(
            "Error: 'cookie', 'pid', or 'imgbb_api_key' not found in 'sportscult.conf'."
        )
        sys.exit(1)

    if path.is_dir():
        base_name = path.name
        isdir = True
        video_files = sorted(path.glob("*.mp4")) + sorted(path.glob("*.mkv"))
        if not video_files:
            print("No video files found in the directory.")
            sys.exit(1)
        video_file = video_files[0]
    elif path.is_file():
        isdir = False        
        base_name = (
            path.stem
        ) 
        video_file = path
    else:
        print("Invalid input path. Provide a file or directory.")
        sys.exit(1)

    print_banner()

    meta_dir = create_meta_dir(base_name)
    nfo_file = generate_mediainfo(video_file, meta_dir, isdir)   
    screenshot_paths = take_screenshots(video_file, meta_dir, isdir) 
    embedding_codes = upload_screenshots(screenshot_paths, imgbb_api_key)
    thumb_file_path = save_embedding_links(embedding_codes, video_file, meta_dir, isdir)
    torrent_path = generate_torrent(video_file, meta_dir, pid, isdir)

    if auto_confirm:
        print("Proceeding with upload...")
        upload_to_sports_cult(video_file, nfo_file, cookie, user_agent, thumb_file_path, category_id, meta_dir, anonymous, torrent_path, isdir)
    else:
        while True:
            response = input("Everything is ready to upload. Do you want to proceed? (y/n): ").strip().lower()
            if response == "y":
                print("Proceeding with upload...")
                upload_to_sports_cult(video_file, nfo_file, cookie, user_agent, thumb_file_path, category_id, meta_dir, anonymous, torrent_path, isdir)
                break
            elif response == "n":
                print("Upload cancelled.")
                break
            else:
                print("Invalid response. Please answer 'y' or 'n'.")


if __name__ == "__main__":
    main()
