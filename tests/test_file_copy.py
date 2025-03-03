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

    def create_nested_directory(self, root_files, nested_files):
        """Helper method to create a nested directory structure with files"""
        # Create root files
        root_paths = self.create_test_files(root_files)
        
        # Create nested directory and its files
        nested_dir = os.path.join(self.temp_dir, 'nested')
        os.makedirs(nested_dir)
        nested_paths = []
        
        for file in nested_files:
            file_path = os.path.join(nested_dir, file)
            with open(file_path, 'w') as f:
                f.write('test content')
            nested_paths.append(file_path)
            
        return root_paths + nested_paths
            
    def test_should_handle_file_images(self):
        self.file_copy.file_type = FileType.IMAGES
        
        # Test valid image extensions
        self.assertTrue(self.file_copy._should_handle_file('test.jpg'))
        self.assertTrue(self.file_copy._should_handle_file('test.png'))
        self.assertTrue(self.file_copy._should_handle_file('test.jpeg'))
        
        # Test invalid extensions
        self.assertFalse(self.file_copy._should_handle_file('test.mp4'))
        self.assertFalse(self.file_copy._should_handle_file('test.txt'))
        
    def test_should_handle_file_videos(self):
        self.file_copy.file_type = FileType.VIDEOS
        
        # Test valid video extensions
        self.assertTrue(self.file_copy._should_handle_file('test.mp4'))
        self.assertTrue(self.file_copy._should_handle_file('test.avi'))
        self.assertTrue(self.file_copy._should_handle_file('test.mov'))
        
        # Test invalid extensions
        self.assertFalse(self.file_copy._should_handle_file('test.jpg'))
        self.assertFalse(self.file_copy._should_handle_file('test.txt'))
        
    def test_should_handle_file_images_videos(self):
        self.file_copy.file_type = FileType.IMAGES_VIDEOS
        
        # Test valid extensions
        self.assertTrue(self.file_copy._should_handle_file('test.jpg'))
        self.assertTrue(self.file_copy._should_handle_file('test.mp4'))
        self.assertTrue(self.file_copy._should_handle_file('test.png'))
        self.assertTrue(self.file_copy._should_handle_file('test.avi'))
        
        # Test invalid extensions
        self.assertFalse(self.file_copy._should_handle_file('test.txt'))
        
    def test_should_handle_file_custom(self):
        self.file_copy.file_type = FileType.CUSTOM
        self.file_copy.custom_file_types = ('.txt', '.doc')
        
        # Test valid custom extensions
        self.assertTrue(self.file_copy._should_handle_file('test.txt'))
        self.assertTrue(self.file_copy._should_handle_file('test.doc'))
        
        # Test invalid extensions
        self.assertFalse(self.file_copy._should_handle_file('test.jpg'))
        self.assertFalse(self.file_copy._should_handle_file('test.mp4'))

    def test_find_files_to_copy_empty_directory(self):
        # Configure FileCopy
        self.file_copy.file_type = FileType.IMAGES
        dest_folder = os.path.join(self.temp_dir, 'dest')
        
        # Test with empty directory
        found_files = self.file_copy._find_files_to_copy(self.temp_dir, dest_folder)
        self.assertEqual(len(found_files), 0)
        
    def test_find_files_to_copy_with_mixed_files(self):
        # Create test files
        test_files = ['test1.jpg', 'test2.png', 'test3.txt', 'test4.mp4']
        created_files = self.create_test_files(test_files)
        
        # Configure FileCopy
        self.file_copy.file_type = FileType.IMAGES
        dest_folder = os.path.join(self.temp_dir, 'dest')
        
        # Get the files that were found
        found_files = self.file_copy._find_files_to_copy(self.temp_dir, dest_folder)
        
        # We should only find the image files
        expected_files = [f for f in created_files if os.path.basename(f).lower().endswith(('.jpg', '.png'))]
        self.assertEqual(sorted(found_files), sorted(expected_files))

    def test_find_files_to_copy_nested_directories(self):
        # Create nested directory structure with mixed file types
        root_files = ['root1.jpg', 'root2.txt']
        nested_files = ['nested1.jpg', 'nested2.png', 'nested3.txt']
        all_files = self.create_nested_directory(root_files, nested_files)
        
        # Configure FileCopy
        self.file_copy.file_type = FileType.IMAGES
        dest_folder = os.path.join(self.temp_dir, 'dest')
        
        # Get found files
        found_files = self.file_copy._find_files_to_copy(self.temp_dir, dest_folder)
        
        # Should find only image files from both directories
        expected_files = [f for f in all_files if os.path.basename(f).lower().endswith(('.jpg', '.png'))]
        self.assertEqual(sorted(found_files), sorted(expected_files))

    def test_find_files_to_copy_excludes_destination(self):
        # Create files in source
        source_files = ['test1.jpg', 'test2.png']
        source_paths = self.create_test_files(source_files)
        
        # Create destination folder with files that should be excluded
        dest_folder = os.path.join(self.temp_dir, 'dest')
        os.makedirs(dest_folder)
        dest_file = os.path.join(dest_folder, 'dest.jpg')
        with open(dest_file, 'w') as f:
            f.write('test content')
            
        # Configure FileCopy
        self.file_copy.file_type = FileType.IMAGES
        
        # Get found files
        found_files = self.file_copy._find_files_to_copy(self.temp_dir, dest_folder)
        
        # Should only include source files, not destination files
        self.assertEqual(sorted(found_files), sorted(source_paths))


