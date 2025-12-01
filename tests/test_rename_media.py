#!/usr/bin/env python3
"""
Unit tests for rename_media.py
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))
from rename_media import MediaRenamer


class TestMediaRenamer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.renamer = MediaRenamer(dry_run=True, quiet=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str) -> Path:
        """Helper to create a test file"""
        filepath = self.test_path / filename
        filepath.touch()
        return filepath
    
    def test_generate_new_filename_basic(self):
        """Test basic filename generation"""
        filepath = Path("IMG_1234.jpg")
        capture_dt = datetime(2024, 12, 1, 14, 30, 45)
        existing_names = set()
        
        new_name = self.renamer.generate_new_filename(filepath, capture_dt, existing_names)
        
        self.assertEqual(new_name, "2024-12-01_143045_IMG_1234.jpg")
    
    def test_generate_new_filename_collision(self):
        """Test filename generation with collision"""
        filepath = Path("IMG_1234.jpg")
        capture_dt = datetime(2024, 12, 1, 14, 30, 45)
        existing_names = {"2024-12-01_143045_IMG_1234.jpg"}
        
        new_name = self.renamer.generate_new_filename(filepath, capture_dt, existing_names)
        
        self.assertEqual(new_name, "2024-12-01_143045_IMG_1234_1.jpg")
    
    def test_generate_new_filename_multiple_collisions(self):
        """Test filename generation with multiple collisions"""
        filepath = Path("IMG_1234.jpg")
        capture_dt = datetime(2024, 12, 1, 14, 30, 45)
        existing_names = {
            "2024-12-01_143045_IMG_1234.jpg",
            "2024-12-01_143045_IMG_1234_1.jpg",
            "2024-12-01_143045_IMG_1234_2.jpg"
        }
        
        new_name = self.renamer.generate_new_filename(filepath, capture_dt, existing_names)
        
        self.assertEqual(new_name, "2024-12-01_143045_IMG_1234_3.jpg")
    
    def test_generate_new_filename_preserves_extension(self):
        """Test that file extension is preserved"""
        test_cases = [
            ("photo.HEIC", "2024-12-01_143045_photo.HEIC"),
            ("video.MP4", "2024-12-01_143045_video.MP4"),
            ("image.png", "2024-12-01_143045_image.png"),
        ]
        
        capture_dt = datetime(2024, 12, 1, 14, 30, 45)
        existing_names = set()
        
        for filename, expected in test_cases:
            filepath = Path(filename)
            new_name = self.renamer.generate_new_filename(filepath, capture_dt, existing_names)
            self.assertEqual(new_name, expected)
    
    def test_find_media_files_images(self):
        """Test finding image files"""
        self.create_test_file("photo1.jpg")
        self.create_test_file("photo2.png")
        self.create_test_file("photo3.heic")
        self.create_test_file("document.txt")
        
        files = self.renamer.find_media_files(self.test_path)
        
        self.assertEqual(len(files), 3)
        self.assertTrue(all(f.suffix.lower() in {'.jpg', '.png', '.heic'} for f in files))
    
    def test_find_media_files_videos(self):
        """Test finding video files"""
        self.create_test_file("video1.mp4")
        self.create_test_file("video2.mov")
        self.create_test_file("video3.avi")
        self.create_test_file("notes.docx")
        
        files = self.renamer.find_media_files(self.test_path)
        
        self.assertEqual(len(files), 3)
        self.assertTrue(all(f.suffix.lower() in {'.mp4', '.mov', '.avi'} for f in files))
    
    def test_find_media_files_mixed(self):
        """Test finding mixed media files"""
        self.create_test_file("photo.jpg")
        self.create_test_file("video.mp4")
        self.create_test_file("readme.txt")
        self.create_test_file("screenshot.png")
        
        files = self.renamer.find_media_files(self.test_path)
        
        self.assertEqual(len(files), 3)
    
    def test_find_media_files_recursive(self):
        """Test finding files recursively"""
        self.create_test_file("root.jpg")
        
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.png").touch()
        
        files = self.renamer.find_media_files(self.test_path, recursive=True)
        
        self.assertEqual(len(files), 2)
    
    def test_find_media_files_non_recursive(self):
        """Test finding files non-recursively"""
        self.create_test_file("root.jpg")
        
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.png").touch()
        
        files = self.renamer.find_media_files(self.test_path, recursive=False)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "root.jpg")
    
    def test_stats_initialization(self):
        """Test that stats are properly initialized"""
        self.assertEqual(self.renamer.stats['total'], 0)
        self.assertEqual(self.renamer.stats['renamed'], 0)
        self.assertEqual(self.renamer.stats['skipped'], 0)
        self.assertEqual(self.renamer.stats['errors'], 0)
    
    def test_parse_video_date_formats(self):
        """Test parsing various video date formats"""
        test_cases = [
            ("2024-12-01 14:30:45", datetime(2024, 12, 1, 14, 30, 45)),
            ("2024-12-01T14:30:45", datetime(2024, 12, 1, 14, 30, 45)),
            ("2024-12-01 14:30:45 UTC", datetime(2024, 12, 1, 14, 30, 45)),
        ]
        
        for date_str, expected in test_cases:
            result = self.renamer._parse_video_date(date_str)
            self.assertEqual(result, expected)
    
    def test_parse_video_date_invalid(self):
        """Test parsing invalid video dates"""
        result = self.renamer._parse_video_date("invalid date")
        self.assertIsNone(result)
    
    @patch('rename_media.Image.open')
    def test_extract_image_datetime_success(self, mock_open):
        """Test successful EXIF datetime extraction"""
        mock_image = MagicMock()
        mock_image._getexif.return_value = {
            36867: "2024:12:01 14:30:45"  # DateTimeOriginal tag
        }
        mock_open.return_value = mock_image
        
        filepath = self.create_test_file("test.jpg")
        result = self.renamer.extract_image_datetime(filepath)
        
        self.assertEqual(result, datetime(2024, 12, 1, 14, 30, 45))
    
    @patch('rename_media.Image.open')
    def test_extract_image_datetime_no_exif(self, mock_open):
        """Test EXIF extraction when no EXIF data exists"""
        mock_image = MagicMock()
        mock_image._getexif.return_value = None
        mock_open.return_value = mock_image
        
        filepath = self.create_test_file("test.jpg")
        result = self.renamer.extract_image_datetime(filepath)
        
        self.assertIsNone(result)
    
    def test_get_file_datetime_fallback(self):
        """Test fallback to file creation time"""
        filepath = self.create_test_file("test.txt")
        
        result = self.renamer.get_file_datetime(filepath)
        
        self.assertIsInstance(result, datetime)
        self.assertIsNotNone(result)
    
    def test_plan_renames_skip_already_correct(self):
        """Test that already correctly named files are skipped"""
        capture_dt = datetime(2024, 12, 1, 14, 30, 45)
        correct_name = "2024-12-01_143045_test.jpg"
        filepath = self.create_test_file(correct_name)
        
        with patch.object(self.renamer, 'get_file_datetime', return_value=capture_dt):
            rename_plan = self.renamer.plan_renames([filepath])
        
        self.assertEqual(len(rename_plan), 0)
        self.assertEqual(self.renamer.stats['skipped'], 1)


class TestMediaRenamerIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_dry_run_does_not_rename(self):
        """Test that dry-run mode doesn't actually rename files"""
        test_file = self.test_path / "test.jpg"
        test_file.touch()
        
        renamer = MediaRenamer(dry_run=True, quiet=True)
        renamer.process_directory(self.test_path)
        
        self.assertTrue(test_file.exists())
        self.assertEqual(len(list(self.test_path.glob("*.jpg"))), 1)
    
    def test_empty_directory(self):
        """Test processing an empty directory"""
        renamer = MediaRenamer(dry_run=True, quiet=True)
        renamer.process_directory(self.test_path)
        
        self.assertEqual(renamer.stats['total'], 0)


class TestFileExtensions(unittest.TestCase):
    """Test supported file extension detection"""
    
    def test_image_extensions(self):
        """Test all supported image extensions"""
        from rename_media import IMAGE_EXTENSIONS
        
        expected_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.heif', 
                             '.tiff', '.tif', '.cr2', '.nef', '.arw', '.dng',
                             '.gif', '.bmp', '.webp'}
        
        self.assertEqual(IMAGE_EXTENSIONS, expected_extensions)
    
    def test_video_extensions(self):
        """Test all supported video extensions"""
        from rename_media import VIDEO_EXTENSIONS
        
        expected_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', 
                             '.wmv', '.flv', '.webm', '.mpg', '.mpeg', 
                             '.3gp', '.mts', '.m2ts'}
        
        self.assertEqual(VIDEO_EXTENSIONS, expected_extensions)


if __name__ == '__main__':
    unittest.main()