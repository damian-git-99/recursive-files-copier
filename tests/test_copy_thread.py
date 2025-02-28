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
    for file in test_files:
        filename = os.path.basename(file)
        assert os.path.exists(os.path.join(dest_dir, filename))

def test_compressed_copy(setup_test_env):
    # Arrange
    test_files = setup_test_env["test_files"]
    dest_dir = setup_test_env["dest_dir"]
    
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
        assert len(zip_files) == len(test_files)

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

def test_duplicate_filenames(setup_test_env):
    # Arrange
    test_files = setup_test_env["test_files"]
    dest_dir = setup_test_env["dest_dir"]
    
    # Create a duplicate file scenario
    if test_files:
        duplicate_file = test_files[0]
        filename = os.path.basename(duplicate_file)
        # Pre-create a file with the same name in destination
        with open(os.path.join(dest_dir, filename), 'w') as f:
            f.write('dummy content')
    
    thread = CopyThread(test_files, str(dest_dir), compress_after_copy=False)
    thread.finished = MagicMock()
    thread.progress_changed = MagicMock()
    
    # Act
    thread.run()
    
    # Assert
    assert thread.finished.emit.called
    # Verify the file was copied with a different name
    if test_files:
        filename = os.path.basename(test_files[0])
        name, ext = os.path.splitext(filename)
        assert os.path.exists(os.path.join(dest_dir, f"{name}_1{ext}"))

def test_duplicate_filenames_in_zip(setup_test_env):
    # Arrange
    test_files = setup_test_env["test_files"]
    dest_dir = setup_test_env["dest_dir"]
    
    # Create duplicate files in the test files list
    if test_files:
        duplicate_file = test_files[0]
        filename = os.path.basename(duplicate_file)
        new_path = os.path.join(setup_test_env["source_dir"], f"copy_of_{filename}")
        shutil.copy2(duplicate_file, new_path)
        test_files.append(new_path)
    
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
        # Check that we have the expected number of files
        assert len(files) == len(test_files)
        # Check that all filenames are unique
        assert len(files) == len(set(files))

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