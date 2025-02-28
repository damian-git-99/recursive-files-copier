import unittest
from unittest.mock import Mock, patch
import os
import tempfile
import shutil
from src.file_copy import FileCopy, FileType, CopyOptions

class TestFileCopy(unittest.TestCase):
    def setUp(self):
        self.file_copy = FileCopy()
        # Mock all signals
        self.file_copy.progress_changed = Mock()
        self.file_copy.not_files_found = Mock()
        self.file_copy.copy_finished = Mock()
        self.file_copy.copy_canceled = Mock()
        self.file_copy.show_message = Mock()
        
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.temp_dir)
        
    def create_test_files(self, files):
        """Helper method to create test files in temporary directory"""
        created_files = []
        for file in files:
            file_path = os.path.join(self.temp_dir, file)
            with open(file_path, 'w') as f:
                f.write('test content')
            created_files.append(file_path)
        return created_files
            
    def test_should_handle_file_images(self):
        self.file_copy.file_type = FileType.IMAGES
        
        # Test valid image extensions
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.jpg'))
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.png'))
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.jpeg'))
        
        # Test invalid extensions
        self.assertFalse(self.file_copy._FileCopy__should_handle_file('test.mp4'))
        self.assertFalse(self.file_copy._FileCopy__should_handle_file('test.txt'))
        
    def test_should_handle_file_videos(self):
        self.file_copy.file_type = FileType.VIDEOS
        
        # Test valid video extensions
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.mp4'))
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.avi'))
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.mov'))
        
        # Test invalid extensions
        self.assertFalse(self.file_copy._FileCopy__should_handle_file('test.jpg'))
        self.assertFalse(self.file_copy._FileCopy__should_handle_file('test.txt'))
        
    def test_should_handle_file_images_videos(self):
        self.file_copy.file_type = FileType.IMAGES_VIDEOS
        
        # Test valid extensions
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.jpg'))
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.mp4'))
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.png'))
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.avi'))
        
        # Test invalid extensions
        self.assertFalse(self.file_copy._FileCopy__should_handle_file('test.txt'))
        
    def test_should_handle_file_custom(self):
        self.file_copy.file_type = FileType.CUSTOM
        self.file_copy.custom_file_types = ('.txt', '.doc')
        
        # Test valid custom extensions
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.txt'))
        self.assertTrue(self.file_copy._FileCopy__should_handle_file('test.doc'))
        
        # Test invalid extensions
        self.assertFalse(self.file_copy._FileCopy__should_handle_file('test.jpg'))
        self.assertFalse(self.file_copy._FileCopy__should_handle_file('test.mp4'))
        
    @patch('src.file_copy.CopyThread')
    def test_find_files_to_copy_images(self, mock_copy_thread):
        # Setup
        test_files = ['test1.jpg', 'test2.png', 'test3.txt', 'test4.mp4']
        created_files = self.create_test_files(test_files)
        
        # Configure FileCopy
        options = CopyOptions(
            source=self.temp_dir,
            file_type=FileType.IMAGES,
            compress_after_copy=False,
            custom_file_types=None
        )
        self.file_copy.start_copy(options)
        
        # Get the files that were found (excluding the created destination folder)
        found_files = [f for f in self.file_copy._FileCopy__find_files_to_copy()]
        
        # We should only find the image files
        expected_files = [f for f in created_files if f.endswith(('.jpg', '.png'))]
        self.assertEqual(sorted(found_files), sorted(expected_files))
        
    @patch('src.file_copy.CopyThread')
    def test_find_files_to_copy_empty_directory(self, mock_copy_thread):
        # Configure FileCopy with empty directory
        options = CopyOptions(
            source=self.temp_dir,
            file_type=FileType.IMAGES,
            compress_after_copy=False,
            custom_file_types=None
        )
        self.file_copy.start_copy(options)
        
        # Should find no files
        found_files = self.file_copy._FileCopy__find_files_to_copy()
        self.assertEqual(len(found_files), 0)
        
    @patch('src.file_copy.CopyThread')
    def test_find_files_to_copy_nested_directories(self, mock_copy_thread):
        # Create nested directory structure
        nested_dir = os.path.join(self.temp_dir, 'nested')
        os.makedirs(nested_dir)
        
        # Create files in both root and nested directory
        root_files = ['root1.jpg', 'root2.txt']
        nested_files = ['nested1.jpg', 'nested2.png']
        
        self.create_test_files(root_files)
        for file in nested_files:
            file_path = os.path.join(nested_dir, file)
            with open(file_path, 'w') as f:
                f.write('test content')
        
        # Configure FileCopy
        options = CopyOptions(
            source=self.temp_dir,
            file_type=FileType.IMAGES,
            compress_after_copy=False,
            custom_file_types=None
        )
        self.file_copy.start_copy(options)
        
        # Get found files
        found_files = self.file_copy._FileCopy__find_files_to_copy()
        
        # Should find both root and nested image files
        self.assertEqual(len(found_files), 3)  # root1.jpg, nested1.jpg, nested2.png
        self.assertTrue(any('root1.jpg' in f for f in found_files))
        self.assertTrue(any('nested1.jpg' in f for f in found_files))
        self.assertTrue(any('nested2.png' in f for f in found_files))
