arize uploads to Sports Cult

## **What does it do?**

* Generates media info of the file

* Takes screenshots and host them automatically on imgbb

* Uploads the torrent to Sports Cult

* Start seeding on qBitorrent automatically

## Setup:

1. Clone this repo to your system
   
   `git clone https://github.com/costaht/SportsCult-Uploader.git`

2. Create a python virtual environment into the newly created directory
   
   `cd SportsCult-Uploader`
   `python -m venv venv`

3. Activate the venv and install the requirements
   
   `source venv/bin/activate` # Linux
   `.\venv\Scripts\activate` # Windows
   `pip install -U -r requirements.txt`

4. Install the external dependencies `[ffmpeg](https://windowsloop.com/install-ffmpeg-windows-10/)` and `mediainfo`

5. Fill up the the config file `sportscult.conf`

6. 

## Usage:

1. Go to SportsCult-Uploader directory

2. Activate the virtual environment
   
   `source venv/bin/activate` # Linux
   
   `.\venv\Scripts\activate` # Windows

3. Run the command:
   
   `python upload.py -c uploadCategory VideoFile.mkv/Folder`

Use `--help` for more details

## Attention:

* Folders will be treated as Season. A single torrent will be created to the entire folder.

* Categories that have space in them should be "beteween quotes"
