# Media File Renamer

A cross-platform Python script that renames photos and videos based on their capture date/time from EXIF metadata.

## Features

✅ **Smart Date Detection**
- Extracts EXIF data from images (JPG, PNG, HEIC, TIFF, RAW formats)
- Reads metadata from videos (MP4, MOV, AVI, MKV, etc.)
- Falls back to file creation date when metadata is unavailable

✅ **Intelligent Naming**
- Format: `YYYY-MM-DD_HHMMSS_OriginalName.ext`
- Example: `2024-12-01_143045_IMG_1234.jpg`
- Preserves original filename to handle timestamp collisions

✅ **Safe Operations**
- Dry-run mode to preview changes before executing
- Comprehensive error handling
- Detailed logging with multiple verbosity levels
- Progress tracking for batch operations

✅ **Cross-Platform**
- Works on Windows 11, Linux, and macOS
- Uses Python's `pathlib` for portable path handling

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

### Optional: Install pymediainfo

For enhanced video metadata extraction:

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libmediainfo-dev
pip install pymediainfo
```

**macOS:**
```bash
brew install media-info
pip install pymediainfo
```

**Windows 11:**
1. Download and install MediaInfo from https://mediaarea.net/en/MediaInfo
2. Install pymediainfo:
```cmd
pip install pymediainfo
```

## Windows 11 Setup Guide

### Command Prompt (CMD) Setup

1. **Install Python**
   - Download Python 3.11+ from https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation
   - Verify installation:
   ```cmd
   python --version
   pip --version
   ```

2. **Clone or Download Repository**
   ```cmd
   cd %USERPROFILE%\Documents
   git clone https://github.com/dandyrandy84/rename-media-script.git
   cd rename-media-script
   ```
   
   Or extract downloaded ZIP to `C:\Users\YourUsername\Documents\rename-media-script`

3. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the Script**
   ```cmd
   rem Dry run to preview changes
   python rename_media.py "C:\Users\YourUsername\Pictures\MyPhotos" --dry-run
   
   rem Actual rename
   python rename_media.py "C:\Users\YourUsername\Pictures\MyPhotos"
   
   rem Recursive with verbose output
   python rename_media.py "C:\Users\YourUsername\Pictures" --recursive -v
   ```

### PyCharm Setup

1. **Install PyCharm Community Edition**
   - Download from https://www.jetbrains.com/pycharm/download/#section=windows
   - Install with default settings

2. **Open Project in PyCharm**
   - Launch PyCharm
   - File → Open
   - Navigate to `C:\Users\YourUsername\Documents\rename-media-script`
   - Click "OK"

3. **Configure Python Interpreter**
   - File → Settings (Ctrl+Alt+S)
   - Project: rename-media-script → Python Interpreter
   - Click ⚙️ icon → Add Interpreter → Add Local Interpreter
   - Select "System Interpreter" or create a new virtual environment
   - Click "OK"

4. **Install Dependencies in PyCharm**
   - Open Terminal in PyCharm (View → Tool Windows → Terminal or Alt+F12)
   - Run:
   ```cmd
   pip install -r requirements.txt
   ```

5. **Create Run Configuration**
   
   **Method A: Using PyCharm Run Configuration**
   - Right-click `rename_media.py` in Project panel
   - Run 'rename_media'
   - Run → Edit Configurations
   - Add parameters:
     ```
     C:\Users\YourUsername\Pictures\MyPhotos --dry-run
     ```
   - Click "OK" and run with ▶️ (Shift+F10)
   
   **Method B: Using PyCharm Terminal**
   - Open Terminal in PyCharm (Alt+F12)
   - Run commands:
   ```cmd
   rem Preview changes
   python rename_media.py "C:\Users\YourUsername\Pictures\MyPhotos" --dry-run
   
   rem Execute rename
   python rename_media.py "C:\Users\YourUsername\Pictures\MyPhotos"
   
   rem Process all subdirectories with verbose output
   python rename_media.py "C:\Users\YourUsername\Pictures" --recursive -v
   ```

6. **View Output**
   - Run panel shows all console output
   - Green messages = successful renames
   - Yellow warnings = skipped files
   - Red errors = failed operations

### Windows-Specific Tips

1. **Path Handling**
   - Always use quotes around paths with spaces: `"C:\My Photos\Vacation"`
   - Forward slashes work too: `C:/Users/YourUsername/Pictures`
   - Use raw strings in Python: `r"C:\Users\YourUsername\Pictures"`

2. **Git Setup for Windows**
   - Download Git from https://git-scm.com/download/win
   - Use Git Bash or Git GUI for version control
   - In PyCharm: VCS → Enable Version Control Integration → Git

3. **Running from File Explorer**
   - Right-click `rename_media.py`
   - Open With → Python
   - Note: This requires modifying the script to accept input interactively
   
4. **Scheduled Tasks**
   Create a batch file `rename_photos.bat`:
   ```cmd
   @echo off
   cd C:\Users\YourUsername\Documents\rename-media-script
   python rename_media.py "C:\Users\YourUsername\Pictures\Auto-Import" --recursive -q
   pause
   ```
   Then schedule it via Task Scheduler for automatic processing

## Usage

### Basic Usage

Rename all media files in a directory (dry-run mode):
```bash
python rename_media.py /path/to/photos --dry-run
```

Perform actual rename:
```bash
python rename_media.py /path/to/photos
```

### Command-Line Options

```
usage: rename_media.py [-h] [--dry-run] [-r] [-v] [-q] directory

Rename media files based on capture date/time from EXIF metadata

positional arguments:
  directory        Directory containing media files to rename

options:
  -h, --help       show this help message and exit
  --dry-run        Preview changes without actually renaming files
  -r, --recursive  Process subdirectories recursively
  -v, --verbose    Enable verbose logging (debug level)
  -q, --quiet      Suppress informational messages (errors only)
```

### Examples

**1. Preview changes before renaming:**
```bash
python rename_media.py ~/Pictures/Vacation --dry-run
```

**2. Rename files with verbose output:**
```bash
python rename_media.py ~/Pictures/Vacation -v
```

**3. Recursively rename files in all subdirectories:**
```bash
python rename_media.py ~/Pictures --recursive
```

**4. Quiet mode (errors only):**
```bash
python rename_media.py ~/Pictures/Vacation -q
```

**5. Combine options:**
```bash
python rename_media.py ~/Pictures --recursive --dry-run -v
```

## Supported File Formats

### Images
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- HEIC/HEIF (`.heic`, `.heif`)
- TIFF (`.tiff`, `.tif`)
- GIF (`.gif`)
- BMP (`.bmp`)
- WebP (`.webp`)
- RAW formats (`.cr2`, `.nef`, `.arw`, `.dng`)

### Videos
- MP4 (`.mp4`)
- MOV (`.mov`)
- AVI (`.avi`)
- MKV (`.mkv`)
- M4V (`.m4v`)
- WMV (`.wmv`)
- FLV (`.flv`)
- WebM (`.webm`)
- MPEG (`.mpg`, `.mpeg`)
- 3GP (`.3gp`)
- MTS/M2TS (`.mts`, `.m2ts`)

## How It Works

1. **Scan Directory**: Finds all media files in the specified directory
2. **Extract Metadata**: For each file, attempts to extract capture date/time from:
   - Image EXIF data (DateTimeOriginal, DateTimeDigitized, or DateTime tags)
   - Video metadata (encoded_date, tagged_date, or recorded_date)
   - File creation timestamp (fallback)
3. **Generate Names**: Creates new filename in format `YYYY-MM-DD_HHMMSS_OriginalName.ext`
4. **Handle Collisions**: If multiple files have the same timestamp, preserves original filename
5. **Execute Renames**: Renames files (or previews in dry-run mode)
6. **Report Results**: Displays summary of operations

## Output Format

The script renames files to this format:
```
YYYY-MM-DD_HHMMSS_OriginalName.ext
```

Examples:
- `IMG_1234.jpg` → `2024-12-01_143045_IMG_1234.jpg`
- `VID_5678.mp4` → `2024-12-01_153020_VID_5678.mp4`
- `photo.heic` → `2024-11-30_091500_photo.heic`

### Collision Handling

If multiple files have identical timestamps, the script preserves the original filename to avoid conflicts:

```
2024-12-01_143045_IMG_1234.jpg
2024-12-01_143045_IMG_1235.jpg
2024-12-01_143045_IMG_1236.jpg
```

## Logging Levels

The script provides three logging levels:

- **Normal** (default): Shows rename operations and summary
- **Verbose** (`-v`): Shows detailed metadata extraction and processing steps
- **Quiet** (`-q`): Shows only errors

## Safety Features

1. **Dry-Run Mode**: Preview all changes before executing
2. **Collision Detection**: Prevents overwriting existing files
3. **Error Recovery**: Continues processing even if individual files fail
4. **Detailed Logging**: Track what changes were made
5. **Summary Report**: Shows statistics for the entire operation

## Example Output

```
INFO: Scanning directory: /Users/john/Pictures/Vacation
INFO: Found 42 media files
INFO: Planning rename operations...
INFO: Planning to rename 38 files
INFO: [1/38] IMG_1234.jpg → 2024-12-01_143045_IMG_1234.jpg
INFO: [2/38] IMG_1235.jpg → 2024-12-01_143046_IMG_1235.jpg
...
INFO: 
==================================================
SUMMARY
==================================================
INFO: Total files found:    42
INFO: Files renamed:        38
INFO: Files skipped:        4
INFO: Errors:               0
```

## Troubleshooting

### pymediainfo not found
If you see warnings about pymediainfo:
- Video metadata extraction will be limited
- The script will still work using file timestamps for videos
- Install pymediainfo (see Installation section) for full video support

### No EXIF data found
- Some images may not contain EXIF data (edited photos, screenshots)
- The script will use the file creation/modification date as fallback

### Permission errors
- Ensure you have write permissions for the target directory
- On Linux/macOS, you may need to use `sudo` for system directories (not recommended)

### Files already renamed
- The script skips files that already match the target format
- These are counted in "Files skipped" in the summary

## Development

### Project Structure
```
rename-media-script/
├── rename_media.py          # Main script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── ARCHITECTURE.md         # Technical documentation
├── .gitignore             # Git ignore rules
└── tests/                 # Unit tests (coming soon)
    └── test_rename_media.py
```

### Running Tests
```bash
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.

## Author

Created to help organize photo and video collections by capture date.

## Version History

- **1.0.0** (2024-12-01): Initial release
  - EXIF metadata extraction for images
  - Video metadata support
  - Dry-run mode
  - Comprehensive logging
  - Cross-platform support