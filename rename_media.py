#!/usr/bin/env python3
"""
Media File Renamer
Renames photos and videos based on capture date/time from EXIF metadata.
Format: YYYY-MM-DD_HHMMSS_OriginalName.ext
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
from collections import defaultdict

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    print("Error: Pillow library not found. Install with: pip install Pillow")
    sys.exit(1)

try:
    from pymediainfo import MediaInfo
except ImportError:
    MediaInfo = None
    print("Warning: pymediainfo not found. Video metadata extraction will be limited.")
    print("Install with: pip install pymediainfo")


IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.tiff', '.tif', 
                    '.cr2', '.nef', '.arw', '.dng', '.gif', '.bmp', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', 
                    '.webm', '.mpg', '.mpeg', '.3gp', '.mts', '.m2ts'}


class MediaRenamer:
    def __init__(self, dry_run: bool = False, verbose: bool = False, quiet: bool = False):
        self.dry_run = dry_run
        self.setup_logging(verbose, quiet)
        self.stats = {
            'total': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }
        
    def setup_logging(self, verbose: bool, quiet: bool):
        if quiet:
            level = logging.ERROR
        elif verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO
            
        logging.basicConfig(
            level=level,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_image_datetime(self, filepath: Path) -> Optional[datetime]:
        """Extract capture datetime from image EXIF data."""
        try:
            image = Image.open(filepath)
            exif_data = image._getexif()
            
            if not exif_data:
                self.logger.debug(f"No EXIF data found in {filepath.name}")
                return None
            
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                if tag_name in ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']:
                    try:
                        dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                        self.logger.debug(f"Found {tag_name} in {filepath.name}: {dt}")
                        return dt
                    except (ValueError, TypeError) as e:
                        self.logger.debug(f"Error parsing {tag_name}: {e}")
                        continue
            
            self.logger.debug(f"No datetime EXIF tags found in {filepath.name}")
            return None
            
        except Exception as e:
            self.logger.debug(f"Error reading EXIF from {filepath.name}: {e}")
            return None
    
    def extract_video_datetime(self, filepath: Path) -> Optional[datetime]:
        """Extract creation datetime from video metadata."""
        if MediaInfo is None:
            self.logger.debug(f"pymediainfo not available for {filepath.name}")
            return None
            
        try:
            media_info = MediaInfo.parse(str(filepath))
            
            for track in media_info.tracks:
                if track.track_type == "General":
                    encoded_date = getattr(track, 'encoded_date', None)
                    tagged_date = getattr(track, 'tagged_date', None)
                    recorded_date = getattr(track, 'recorded_date', None)
                    
                    for date_field in [encoded_date, tagged_date, recorded_date]:
                        if date_field:
                            try:
                                dt = self._parse_video_date(date_field)
                                if dt:
                                    self.logger.debug(f"Found video datetime in {filepath.name}: {dt}")
                                    return dt
                            except Exception as e:
                                self.logger.debug(f"Error parsing video date: {e}")
                                continue
            
            self.logger.debug(f"No datetime metadata found in video {filepath.name}")
            return None
            
        except Exception as e:
            self.logger.debug(f"Error reading video metadata from {filepath.name}: {e}")
            return None
    
    def _parse_video_date(self, date_str: str) -> Optional[datetime]:
        """Parse various video date formats."""
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%f',
        ]
        
        date_str = str(date_str).split('UTC')[0].strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def get_file_datetime(self, filepath: Path) -> datetime:
        """
        Get datetime for file, preferring EXIF/metadata, falling back to file creation time.
        """
        extension = filepath.suffix.lower()
        
        if extension in IMAGE_EXTENSIONS:
            dt = self.extract_image_datetime(filepath)
            if dt:
                return dt
        
        elif extension in VIDEO_EXTENSIONS:
            dt = self.extract_video_datetime(filepath)
            if dt:
                return dt
        
        stat = filepath.stat()
        creation_time = getattr(stat, 'st_birthtime', stat.st_mtime)
        dt = datetime.fromtimestamp(creation_time)
        self.logger.debug(f"Using file creation time for {filepath.name}: {dt}")
        return dt
    
    def generate_new_filename(self, filepath: Path, capture_dt: datetime, 
                            existing_names: set) -> str:
        """
        Generate new filename in format YYYY-MM-DD_HHMMSS_OriginalName.ext
        Handles collisions by preserving original filename.
        """
        date_prefix = capture_dt.strftime('%Y-%m-%d_%H%M%S')
        original_stem = filepath.stem
        extension = filepath.suffix
        
        new_name = f"{date_prefix}_{original_stem}{extension}"
        
        if new_name not in existing_names:
            return new_name
        
        counter = 1
        while True:
            new_name = f"{date_prefix}_{original_stem}_{counter}{extension}"
            if new_name not in existing_names:
                self.logger.debug(f"Collision resolved: {new_name}")
                return new_name
            counter += 1
    
    def find_media_files(self, directory: Path, recursive: bool = False) -> List[Path]:
        """Find all media files in directory."""
        media_files = []
        all_extensions = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
        
        if recursive:
            pattern = '**/*'
        else:
            pattern = '*'
        
        for filepath in directory.glob(pattern):
            if filepath.is_file() and filepath.suffix.lower() in all_extensions:
                media_files.append(filepath)
        
        return sorted(media_files)
    
    def plan_renames(self, files: List[Path]) -> List[Tuple[Path, Path]]:
        """
        Plan all rename operations, checking for collisions within the rename set.
        Returns list of (old_path, new_path) tuples.
        """
        rename_plan = []
        existing_names = set()
        
        for filepath in files:
            try:
                capture_dt = self.get_file_datetime(filepath)
                new_filename = self.generate_new_filename(filepath, capture_dt, existing_names)
                new_path = filepath.parent / new_filename
                
                if filepath.name == new_filename:
                    self.logger.debug(f"Skipping {filepath.name} - already has correct name")
                    self.stats['skipped'] += 1
                    continue
                
                rename_plan.append((filepath, new_path))
                existing_names.add(new_filename)
                
            except Exception as e:
                self.logger.error(f"Error planning rename for {filepath.name}: {e}")
                self.stats['errors'] += 1
        
        return rename_plan
    
    def execute_renames(self, rename_plan: List[Tuple[Path, Path]]) -> None:
        """Execute the rename operations."""
        total = len(rename_plan)
        
        for idx, (old_path, new_path) in enumerate(rename_plan, 1):
            try:
                if self.dry_run:
                    self.logger.info(f"[DRY RUN] {old_path.name} → {new_path.name}")
                else:
                    if new_path.exists():
                        self.logger.warning(f"Target exists, skipping: {new_path.name}")
                        self.stats['skipped'] += 1
                        continue
                    
                    old_path.rename(new_path)
                    self.logger.info(f"[{idx}/{total}] {old_path.name} → {new_path.name}")
                    self.stats['renamed'] += 1
                    
            except Exception as e:
                self.logger.error(f"Error renaming {old_path.name}: {e}")
                self.stats['errors'] += 1
    
    def process_directory(self, directory: Path, recursive: bool = False) -> None:
        """Main processing function."""
        if not directory.exists():
            self.logger.error(f"Directory does not exist: {directory}")
            sys.exit(1)
        
        if not directory.is_dir():
            self.logger.error(f"Not a directory: {directory}")
            sys.exit(1)
        
        self.logger.info(f"Scanning directory: {directory}")
        media_files = self.find_media_files(directory, recursive)
        
        if not media_files:
            self.logger.info("No media files found")
            return
        
        self.stats['total'] = len(media_files)
        self.logger.info(f"Found {len(media_files)} media files")
        
        self.logger.info("Planning rename operations...")
        rename_plan = self.plan_renames(media_files)
        
        if not rename_plan:
            self.logger.info("No files need renaming")
            return
        
        self.logger.info(f"{'DRY RUN - ' if self.dry_run else ''}Planning to rename {len(rename_plan)} files")
        
        if self.dry_run:
            self.logger.info("\nPreview of changes:")
        
        self.execute_renames(rename_plan)
        
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print operation summary."""
        self.logger.info("\n" + "="*50)
        self.logger.info("SUMMARY")
        self.logger.info("="*50)
        self.logger.info(f"Total files found:    {self.stats['total']}")
        self.logger.info(f"Files renamed:        {self.stats['renamed']}")
        self.logger.info(f"Files skipped:        {self.stats['skipped']}")
        self.logger.info(f"Errors:               {self.stats['errors']}")
        
        if self.dry_run:
            self.logger.info("\nThis was a DRY RUN - no files were actually renamed")
            self.logger.info("Remove --dry-run flag to perform actual renames")


def main():
    parser = argparse.ArgumentParser(
        description='Rename media files based on capture date/time from EXIF metadata',
        epilog='Example: python rename_media.py /path/to/photos --dry-run'
    )
    
    parser.add_argument(
        'directory',
        type=Path,
        help='Directory containing media files to rename'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without actually renaming files'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process subdirectories recursively'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (debug level)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress informational messages (errors only)'
    )
    
    args = parser.parse_args()
    
    if args.verbose and args.quiet:
        print("Error: --verbose and --quiet are mutually exclusive")
        sys.exit(1)
    
    renamer = MediaRenamer(
        dry_run=args.dry_run,
        verbose=args.verbose,
        quiet=args.quiet
    )
    
    try:
        renamer.process_directory(args.directory, args.recursive)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()