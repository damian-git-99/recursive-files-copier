import pytest
import os
import shutil
import zipfile
from unittest.mock import MagicMock
from src.copy_thread import CopyThread

def clean_output_dir():
    """Helper function to clean the output directory before each test"""
    output_dir = "./tests/output"
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            else:
                shutil.rmtree(item_path)

@pytest.fixture
def setup_test_env():
    # Clean and create test directories
    clean_output_dir()
    source_dir = os.path.join("./tests/output", "source")
    dest_dir = os.path.join("./tests/output", "destination")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copy all files from test/images recursively
    test_images_dir = "./tests/images"
    test_files = []
    
    # Walk through all directories and files
    for root, dirs, files in os.walk(test_images_dir):
        # Calculate relative path to maintain directory structure
        rel_path = os.path.relpath(root, test_images_dir)
        
        # Create corresponding directories in source
        if rel_path != '.':
            os.makedirs(os.path.join(source_dir, rel_path), exist_ok=True)
        
        # Copy all files maintaining directory structure
        for file in files:
            src_file_path = os.path.join(root, file)
            if rel_path == '.':
                dest_file_path = os.path.join(source_dir, file)
            else:
                dest_file_path = os.path.join(source_dir, rel_path, file)
            
            shutil.copy2(src_file_path, dest_file_path)
            test_files.append(dest_file_path)
    
    return {
        "source_dir": source_dir,
        "dest_dir": dest_dir,
        "test_files": test_files
    }

def test_normal_copy(setup_test_env):
    # Arrange
    test_files = setup_test_env["test_files"]
    dest_dir = setup_test_env["dest_dir"]
    
    # Get total number of files in images directory
    total_images = 0
    for root, _, files in os.walk("./tests/images"):
        total_images += len(files)
    
    thread = CopyThread(test_files, str(dest_dir), compress_after_copy=False)
    thread.finished = MagicMock()
    thread.progress_changed = MagicMock()
    thread.not_files_found = MagicMock()
    thread.copy_canceled = MagicMock()
    
    # Act
    thread.run()
    
    # Assert
    assert thread.finished.emit.called
    assert thread.progress_changed.emit.called
    assert not thread.not_files_found.emit.called
    assert not thread.copy_canceled.emit.called
    
    # Verify files were copied
    copied_files = []
    for root, _, files in os.walk(dest_dir):
        for file in files:
            copied_files.append(os.path.join(root, file))
    
    # Verify we copied all files from the original structure
    assert len(copied_files) == total_images, f"Expected {total_images} files to be copied, but found {len(copied_files)}"
    
    # Verify each file exists in destination
    for file in test_files:
        filename = os.path.basename(file)
        assert os.path.exists(os.path.join(dest_dir, filename))

def test_compressed_copy(setup_test_env):
    # Arrange
    test_files = setup_test_env["test_files"]
    dest_dir = setup_test_env["dest_dir"]
    
    # Get total number of files in images directory
    total_images = 0
    for root, _, files in os.walk("./tests/images"):
        total_images += len(files)
    
    thread = CopyThread(test_files, str(dest_dir), compress_after_copy=True)
    thread.finished = MagicMock()
    thread.progress_changed = MagicMock()
    thread.not_files_found = MagicMock()
    thread.copy_canceled = MagicMock()
    
    # Act
    thread.run()
    
    # Assert
    assert thread.finished.emit.called
    assert thread.progress_changed.emit.called
    assert not thread.not_files_found.emit.called
    assert not thread.copy_canceled.emit.called
    
    # Verify zip file was created and contains all files
    zip_path = os.path.join(dest_dir, "compressed_files.zip")
    assert os.path.exists(zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zip_files = zipf.namelist()
        # Verify we have all files from the original structure
        assert len(zip_files) == total_images, f"Expected {total_images} files in ZIP, but found {len(zip_files)}"
        # Verify all filenames are unique
        assert len(zip_files) == len(set(zip_files)), "ZIP contains duplicate filenames"

def test_cancel_copy(setup_test_env):
    # Arrange
    test_files = setup_test_env["test_files"]
    dest_dir = setup_test_env["dest_dir"]
    
    thread = CopyThread(test_files, str(dest_dir), compress_after_copy=False)
    thread.finished = MagicMock()
    thread.progress_changed = MagicMock()
    thread.not_files_found = MagicMock()
    thread.copy_canceled = MagicMock()
    
    # Act
    thread.cancel_copy()
    thread.run()
    
    # Assert
    assert not thread.finished.emit.called
    assert thread.copy_canceled.emit.called
    assert not thread.not_files_found.emit.called

def test_duplicate_filenames_in_zip(setup_test_env):
    # Arrange
    test_files = setup_test_env["test_files"]
    dest_dir = setup_test_env["dest_dir"]
    
    thread = CopyThread(test_files, str(dest_dir), compress_after_copy=True)
    thread.finished = MagicMock()
    thread.progress_changed = MagicMock()
    
    # Act
    thread.run()
    
    # Assert
    assert thread.finished.emit.called
    
    # Verify zip contains uniquely named files
    zip_path = os.path.join(dest_dir, "compressed_files.zip")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        files = zipf.namelist()
        # Check that all filenames are unique in the ZIP
        assert len(files) == len(set(files)), "ZIP file contains duplicate filenames"
        # Verify all test files were included
        assert len(files) == len(test_files), "Not all files were included in the ZIP"

def test_recursive_copy(setup_test_env):
    # Arrange
    test_files = setup_test_env["test_files"]
    dest_dir = setup_test_env["dest_dir"]
    
    thread = CopyThread(test_files, str(dest_dir), compress_after_copy=False)
    thread.finished = MagicMock()
    thread.progress_changed = MagicMock()
    thread.not_files_found = MagicMock()
    thread.copy_canceled = MagicMock()
    
    # Act
    thread.run()
    
    # Assert
    assert thread.finished.emit.called
    assert thread.progress_changed.emit.called
    assert not thread.not_files_found.emit.called
    assert not thread.copy_canceled.emit.called
    
    # Verify files were copied and renamed correctly
    copied_files = []
    for root, dirs, files in os.walk(dest_dir):
        for f in files:
            file_path = os.path.join(root, f)
            copied_files.append(file_path)
    
    # Check if all files were copied
    assert len(copied_files) == len(test_files)
    
    # Check for no duplicate filenames in any directory
    for root, dirs, files in os.walk(dest_dir):
        assert len(files) == len(set(files)), f"Found duplicate filenames in {root}"
        
    # Check if files with same names were properly renamed
    dest_filenames = [os.path.basename(f) for f in copied_files]
    assert len(dest_filenames) == len(set(dest_filenames)), "Files were not renamed properly" 