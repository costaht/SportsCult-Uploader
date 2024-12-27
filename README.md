# **Sports Cult Uploader**

A script designed to simplify and standardize the process of uploading content to Sports Cult.

## **Features**

- Automatically generates detailed media information for the file.
- Captures screenshots and hosts them on imgbb.
- Uploads the torrent to Sports Cult.
- Starts seeding automatically on qBittorrent.

---

## **Setup Instructions**

1. **Clone the repository**  
   Run the following command to clone the repository to your system:
   
   ```bash
   git clone https://github.com/costaht/SportsCult-Uploader.git
   ```

2. **Create a Python virtual environment**  
   Navigate to the newly created directory and set up a virtual environment:
   
   ```bash
   cd SportsCult-Uploader
   python -m venv venv
   ```

3. **Activate the virtual environment and install dependencies**
   
   - **Linux**:
     
     ```bash
     source venv/bin/activate
     ```
   
   - **Windows**:
     
     ```bash
     .\venv\Scripts\activate
     ```
   
   Install the required Python packages:

```bash
pip install -U -r requirements.txt
```

4. **Install external dependencies**  
   Download and install the following tools:
   
   - [ffmpeg](https://windowsloop.com/install-ffmpeg-windows-10/)
   - mediainfo

5. **Configure the script**  
   Edit the configuration file `sportscult.conf` with the necessary settings.

---

## **Usage Instructions**

1. **Navigate to the script's directory**
   
   ```bash
   cd SportsCult-Uploader
   ```

2. **Activate the virtual environment**
   
   - **Linux**:
     
     ```bash
     source venv/bin/activate
     ```
   
   - **Windows**:
     
     ```bash
     .\venv\Scripts\activate
     ```

3. **Run the upload command**
   
   ```bash
   python upload.py -c uploadCategory VideoFile.mkv/Folder
   ```
   
   Use the `--help` flag to see additional options and details:
   
   ```bash
   python upload.py --help
   ```

---

## **Important Notes**

- **Folder Handling**:  
  If you specify a folder, the script will treat it as a season and create a single torrent for the entire folder.

- **Category Names with Spaces**:  
  For categories with spaces in their names, enclose the category name in double quotes (e.g., `"Sports Events"`).
