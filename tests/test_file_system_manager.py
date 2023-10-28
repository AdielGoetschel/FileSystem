import os
import textwrap
import unittest
import numpy as np
from io import StringIO
from unittest.mock import patch, MagicMock
from file_system_manager import FileSystemManager, MEM_SIZE, MAX_MEM_SIZE,DEFAULT_FILE_SIZE, MAX_FILE_SIZE\
    , JSON_FILE, NUMPY_FILE
from error_messages import ErrorMessages



class TestFileSystemManager(unittest.TestCase):
    def setUp(self):
        # Create an instance of the FileSystemManager class for testing
        self.file_system_manager = FileSystemManager(check_for_backup_files=False)

    def tearDown(self):
        # Clean up any resources created during the test
        # For example, you can reset the state of your FileSystemManager instance
        self.file_system_manager = None

    def test_create_and_read_file(self):
        # Test for the create and read file functionalities
        file_name = "test_file.txt"
        content = "This is a test file."
        start_root_size = self.file_system_manager.path_handler.root.size

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.create_file_or_dir(file_name, file=True, content=content)
            # Assert that the result is True, indicating success
            self.assertTrue(result)

        # Check if the file content matches what was written (including size)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.read_file(file_name)
            printed_content = mock_stdout.getvalue().strip()
            self.assertEqual(printed_content, content)
            file_node = self.file_system_manager.path_handler.get_node_by_path(file_name)
            self.assertEqual(len(content), file_node.size)
            self.assertEqual(file_node.get_last_modified(), file_node.get_creation_time())
            self.assertEqual(file_node.get_last_modified(), file_node.parent_node.get_last_modified())
            self.assertEqual(file_node.size+start_root_size, file_node.parent_node.size)

    def test_get_size_and_get_times(self):
        # Test for the get_size, get_creation_time and get_last_modified_time functionalities
        file_name = "test_file.txt"
        content = "This is a test file."
        self.file_system_manager.create_file_or_dir(file_name, file=True, content=content)
        file_node = self.file_system_manager.path_handler.get_node_by_path(file_name)
        # Test the get_size method
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.get_size(file_name)
            # Assert the printed result using the captured output
            printed_output = mock_stdout.getvalue().strip()
            self.assertIn(str(file_node.size), printed_output)

        # Test the get_creation_time method
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.get_creation_time(file_name)
            # Assert the printed result using the captured output
            printed_output = mock_stdout.getvalue()
            self.assertIn(file_node.get_creation_time(), printed_output)

        # Test the get_last_modified_time method
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.get_last_modified_time(file_name)
            # Assert the printed result using the captured output
            printed_output = mock_stdout.getvalue()
            self.assertIn(file_node.get_last_modified(), printed_output)

    def test_write_to_file(self):
        # Test writing to an existing file
        file_name = "existing_file.txt"
        initial_content = "Initial content."
        new_content = "This is new content."

        # Create the file with initial content
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.create_file_or_dir(file_name, file=True, content=initial_content)

        # Append new content to the file
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.write_to_file(file_name, new_content, append=True)
        # Assert that the result is True, indicating success
        self.assertTrue(result)
        # Check if the file content and file size match the new content
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.read_file(file_name)
            printed_content = mock_stdout.getvalue().strip()
            self.assertEqual(printed_content, initial_content+new_content)
            file_size = self.file_system_manager.path_handler.get_node_by_path(file_name).size
            self.assertEqual(len(initial_content+new_content), file_size)

        # Write new content to the file (instead of the current content)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.write_to_file(file_name, new_content, append=False)
        # Assert that the result is True, indicating success
        self.assertTrue(result)
        # Check if the file content and file size match the new content
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.read_file(file_name)
            printed_content = mock_stdout.getvalue().strip()
            self.assertEqual(printed_content, new_content)
            file_size = self.file_system_manager.path_handler.get_node_by_path(file_name).size
            self.assertEqual(len(new_content), file_size)

    def test_create_directory(self):
        # Test creating a directory
        dir_name = "test_directory"
        result = self.file_system_manager.create_file_or_dir(dir_name, file=False)
        # Assert that the result is True, indicating success
        self.assertTrue(result)
        # Check the attributes of the created directory node
        dir_node = self.file_system_manager.path_handler.get_node_by_path(path=dir_name)
        self.assertEqual(dir_node.name, dir_name)
        self.assertFalse(dir_node.is_file)
        self.assertEqual(dir_node.get_last_modified(), dir_node.get_creation_time())
        self.assertEqual(dir_node.get_last_modified(), dir_node.parent_node.get_last_modified())

    def test_create_existing_node(self):
        # Test creating a node with the same name as an existing node
        file_name = "existing_file.txt"
        # Create a file with the same name
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.create_file_or_dir(file_name, file=True, content="")

        # Try to create a directory with the same name
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.create_file_or_dir(file_name, file=False)
            # Assert that the result is False, indicating failure
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(ErrorMessages.ExistsError.value, printed_message)
            self.assertIn(file_name, printed_message)

    def test_recursive_directory_creation(self):
        # Test creating directories recursively
        dir_path = "/new_test_directory/sub_directory/sub_sub_directory"

        # Try to create when recursive is false
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.create_file_or_dir(dir_path, file=False, recursive=False)
            # Assert that the result is True, indicating success
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(ErrorMessages.NotFoundError.value, printed_message)
            self.assertIn("new_test_directory", printed_message)
            sub_directory = self.file_system_manager.path_handler.get_node_by_path("/new_test_directory/sub_directory")
            sub_sub_directory = self.file_system_manager.path_handler.get_node_by_path\
                ("/test_directory/sub_directory/sub_sub_directory")
            self.assertFalse(sub_directory)
            self.assertFalse(sub_sub_directory)

        # Create when recursive is true
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.create_file_or_dir(dir_path, file=False, recursive=True)
            # Assert that the result is True, indicating success
            self.assertTrue(result)
            sub_directory = self.file_system_manager.path_handler.get_node_by_path("/new_test_directory/sub_directory")
            sub_sub_directory = self.file_system_manager.path_handler.get_node_by_path\
                ("/new_test_directory/sub_directory/sub_sub_directory")
            self.assertEqual(sub_sub_directory.parent_node, sub_directory)

    def test_delete_non_existing_path(self):
        # Test deleting a non-existing path (should return False)
        path = "/non_existing_path"
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.delete_file_or_dir(path)
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(f"{ErrorMessages.NotFoundError.value}{path}", printed_message)

    def test_delete_existing_file(self):
        # Test deleting an existing file
        file_name = "/file_to_delete.txt"
        self.file_system_manager.create_file_or_dir(file_name, file=True, content="File content")
        # Verify that memory allocation has occurred
        file_node = self.file_system_manager.path_handler.get_node_by_path(file_name)
        file_memory_allocations = file_node.file_memory_allocations.copy()
        self.assertTrue(len(file_memory_allocations) > 0)
        result = self.file_system_manager.delete_file_or_dir(file_name)
        self.assertTrue(result)
        # Verify that the file has been deleted
        file_node = self.file_system_manager.path_handler.get_node_by_path(file_name, show_errors=False)
        self.assertFalse(file_node)
        # Verify that memory has been freed and is available for future use
        for allocation in file_memory_allocations:
            start_index, end_index, _ = allocation
            freed_memory = np.zeros(end_index - start_index)  # Create an array of zeros with the same size
            self.assertTrue(np.array_equal(self.file_system_manager.memory_buffer[start_index:end_index], freed_memory))
            self.assertIn(allocation[:-1], self.file_system_manager.allocation_available)

    def test_delete_existing_directory(self):
        # Test deleting an existing directory with multiple files and subdirectories
        parent_dir = "/parent_dir"
        dir_name = f"{parent_dir}/dir_to_delete"
        file1_path = f"{dir_name}/file1.txt"
        file2_path = f"{dir_name}/file2.txt"
        sub_dir_path = f"{dir_name}/sub_dir"
        sub_file3_path = f"{sub_dir_path}/sub_file.txt"

        # Create a directory with files and subdirectories
        self.file_system_manager.create_file_or_dir(parent_dir, file=False)
        self.file_system_manager.create_file_or_dir(dir_name, file=False)
        self.file_system_manager.create_file_or_dir(file1_path, file=True, content="File 1 content")
        self.file_system_manager.create_file_or_dir(file2_path, file=True, content="File 2 content")
        self.file_system_manager.create_file_or_dir(sub_dir_path, file=False)
        self.file_system_manager.create_file_or_dir(sub_file3_path, file=True, content="Sub-file content")

        # Verify the sizes of the parent directory before deletion
        parent_dir_node = self.file_system_manager.path_handler.get_node_by_path(parent_dir)
        original_parent_size = parent_dir_node.size

        # Verify that memory allocation has occurred for files
        file1_node = self.file_system_manager.path_handler.get_node_by_path(file1_path)
        self.assertTrue(len(file1_node.file_memory_allocations) > 0)
        file1_memory_allocations = file1_node.file_memory_allocations.copy()
        file2_node = self.file_system_manager.path_handler.get_node_by_path(file2_path)
        self.assertTrue(len(file2_node.file_memory_allocations) > 0)
        file2_memory_allocations = file2_node.file_memory_allocations.copy()
        file3_node = self.file_system_manager.path_handler.get_node_by_path(sub_file3_path)
        self.assertTrue(len(file3_node.file_memory_allocations) > 0)
        file3_memory_allocations = file3_node.file_memory_allocations.copy()

        result = self.file_system_manager.delete_file_or_dir(dir_name)
        self.assertTrue(result)

        # Verify that the directory and its contents have been deleted
        dir_node = self.file_system_manager.path_handler.get_node_by_path(dir_name, show_errors=False)
        self.assertFalse(dir_node)
        sub_dir_node = self.file_system_manager.path_handler.get_node_by_path(sub_dir_path, show_errors=False)
        self.assertFalse(sub_dir_node)

        # Verify that the parent directory's size has changed after the deletion
        parent_dir_node = self.file_system_manager.path_handler.get_node_by_path(parent_dir)
        self.assertEqual(parent_dir_node.size, 0)

        # Verify that memory has been freed and is available for future use
        for allocation in file1_memory_allocations:
            start_index, end_index, _ = allocation
            freed_memory = np.zeros(end_index - start_index)
            self.assertTrue(np.array_equal(self.file_system_manager.memory_buffer[start_index:end_index], freed_memory))
            self.assertIn(allocation[:-1], self.file_system_manager.allocation_available)

        for allocation in file2_memory_allocations:
            start_index, end_index, _ = allocation
            freed_memory = np.zeros(end_index - start_index)
            self.assertTrue(np.array_equal(self.file_system_manager.memory_buffer[start_index:end_index], freed_memory))
            self.assertIn(allocation[:-1], self.file_system_manager.allocation_available)

        for allocation in file3_memory_allocations:
            start_index, end_index, _ = allocation
            freed_memory = np.zeros(end_index - start_index)
            self.assertTrue(np.array_equal(self.file_system_manager.memory_buffer[start_index:end_index], freed_memory))
            self.assertIn(allocation[:-1], self.file_system_manager.allocation_available)

    def test_show_current_directory(self):
        # Test the show_current_directory function
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            current_dir = self.file_system_manager.show_current_directory()
            # Assert that the current directory is the root directory initially
            self.assertEqual(current_dir, "/")

    def test_update_current_dir(self):
        # Test the update_current_dir function
        dir_name = "test_directory"

        # Create a directory
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.create_file_or_dir(dir_name, file=False)

        # Change the current directory to the newly created directory
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.update_current_dir(dir_name)
            # Verify that the result is True, indicating success
            self.assertTrue(result)
            current_dir = self.file_system_manager.show_current_directory()
            self.assertEqual(current_dir, f"/{dir_name}")

        # Try to change the current directory to a non existing directory
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.update_current_dir("non_existing_directory")
            # Verify that the result is False, indicating failure
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(ErrorMessages.NotFoundError.value, printed_message)

    def test_go_to_previous_dir(self):
        # Test the go_to_previous_dir function
        dir_name = "test_directory"

        # Create a directory
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.create_file_or_dir(dir_name, file=False)

        # Change the current directory to the newly created directory
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.file_system_manager.update_current_dir(dir_name)

        # Go back to the previous directory
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.go_to_previous_dir()
            # Verify that the result is True, indicating success
            self.assertTrue(result)
            current_dir = self.file_system_manager.show_current_directory()
            self.assertEqual(current_dir, "/")

    def test_tree_to_dict_and_dict_to_tree(self):
        # Test the tree_to_dict method
        # Create a TreeNode and add it to the file_system
        content = "This is a test file."
        child1_path = "/child1"
        file1_path = child1_path + "/file1"
        child2_path = "/child2"
        self.file_system_manager.create_file_or_dir(name=file1_path, file=True, content=content, recursive=True)
        self.file_system_manager.create_file_or_dir(name=child2_path, file=False)

        # Capture the expected values of the file system manager metadata
        excepted_buffer_size = self.file_system_manager.buffer_size
        excepted_next_available_end_buffer_index = self.file_system_manager.next_available_end_buffer_index
        excepted_allocation_available = self.file_system_manager.allocation_available

        # Retrieve specific nodes by path
        root_node = self.file_system_manager.path_handler.root
        child1_node = self.file_system_manager.path_handler.get_node_by_path(child1_path)
        file1_node = self.file_system_manager.path_handler.get_node_by_path(file1_path)
        child2_node = self.file_system_manager.path_handler.get_node_by_path(child2_path)


        # Use the tree_to_dict method to convert the file system to a dictionary
        tree_dict = self.file_system_manager.tree_to_dict(self.file_system_manager.path_handler.root)
        expected_result = {
            "metadata": {
                "buffer_size": excepted_buffer_size,
                "next_available_end_buffer_index": excepted_next_available_end_buffer_index,
                "allocation_available": excepted_allocation_available
            },
            "root": {
                "name": "/",
                "is_file": root_node.is_file,
                "last_modified": root_node.last_modified,
                "creation_time": root_node.creation_time,
                "size": root_node.size,
                "children": [
                    {
                        "name": "child1",
                        "is_file": child1_node.is_file,
                        "last_modified": child1_node.last_modified,
                        "creation_time": child1_node.creation_time,
                        "size":child1_node.size,
                        "children": [
                            {
                                "name": "file1",
                                "is_file": file1_node.is_file,
                                "last_modified": file1_node.last_modified,
                                "creation_time": file1_node.creation_time,
                                "size": file1_node.size,
                                "file_memory_allocations": file1_node.file_memory_allocations
                            }
                        ]
                    },
                    {
                        "name": "child2",
                        "is_file": child2_node.is_file,
                        "last_modified": child2_node.last_modified,
                        "creation_time": child2_node.creation_time,
                        "size": child2_node.size,
                        "children": []
                    }
                ]
            }
        }

        self.assertEqual(tree_dict, expected_result)

        # Delete the directories and the file and restore it from the dict
        excepted_root_size = root_node.size
        self.file_system_manager.delete_file_or_dir(name=child1_path)
        self.file_system_manager.delete_file_or_dir(name=child2_path)

        # Use the dict_to_tree method to convert the dictionary back to a tree structure
        self.file_system_manager.dict_to_tree(tree_dict)
        self.file_system_manager.path_handler.root = self.file_system_manager.root


        root_node = self.file_system_manager.root
        child1_node = self.file_system_manager.path_handler.get_node_by_path(child1_path)
        file1_node = self.file_system_manager.path_handler.get_node_by_path(file1_path)
        child2_node = self.file_system_manager.path_handler.get_node_by_path(child2_path)
        # Assert that the attributes of the retrieved nodes match the expected values
        self.assertEqual(root_node.name, "/")
        self.assertEqual(root_node.size, excepted_root_size)
        self.assertEqual(child1_node.name, "child1")
        self.assertEqual(file1_node.name, "file1")
        self.assertEqual(child2_node.name, "child2")

    def test_create_backup_and_restore_backup(self):
        # Test the create_backup and restore_backup methods
        # Create a TreeNode hierarchy and add it to the file_system
        content = "This is a test file."
        file_name = "/file1"
        dir_name = "/child2"
        self.file_system_manager.create_file_or_dir(name=file_name, file=True, content=content)
        self.file_system_manager.create_file_or_dir(name=dir_name, file=False)

        # Call create_backup to create a backup file
        backup_created = self.file_system_manager.create_backup()
        self.assertTrue(backup_created)
        self.assertTrue(os.path.exists(JSON_FILE))
        self.assertTrue(os.path.exists(NUMPY_FILE))

        # Delete the file and restore from backup
        self.file_system_manager.delete_file_or_dir(file_name)
        self.file_system_manager.restore_backup()
        self.file_system_manager.path_handler.root = self.file_system_manager.root

        # Verify that the TreeNode hierarchy is restored
        self.assertEqual(len(self.file_system_manager.root.children), 2)
        self.assertEqual(self.file_system_manager.root.children[0].name,
                         self.file_system_manager.path_handler.split_path(file_name)[1])
        self.assertEqual(self.file_system_manager.root.children[1].name,
                         self.file_system_manager.path_handler.split_path(dir_name)[1])
        file_node = self.file_system_manager.path_handler.get_node_by_path(file_name)
        self.assertIsNotNone(file_node)
        self.assertTrue(file_node.is_file)
        self.assertEqual(file_node.size, len(content))



    def test_display_directory_content(self):
        # Test displaying an existing directory
        directory_name = "/existing_directory"
        expected_output = ("└── existing_directory" + "\n"
                           "    ├── file1.txt" + "\n"
                           "    ├── file2.txt" + "\n"
                           "    └── subdirectory" + "\n"
                           "        ├── file3.txt" + "\n"
                           "        ├── file4.txt")


        # Create the directory structure with files and subdirectories
        self.file_system_manager.create_file_or_dir(name=directory_name, file=False)
        self.file_system_manager.create_file_or_dir(name=directory_name + "/file1.txt", file=True)
        self.file_system_manager.create_file_or_dir(name=directory_name + "/file2.txt", file=True)
        self.file_system_manager.create_file_or_dir(name=directory_name + "/subdirectory", file=False)
        self.file_system_manager.create_file_or_dir(name=directory_name + "/subdirectory/file3.txt", file=True)
        self.file_system_manager.create_file_or_dir(name=directory_name + "/subdirectory/file4.txt", file=True)

        # Verify that the TreeNode hierarchy is printed
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.display_directory_content(directory_name, recursive=True)
            self.assertTrue(result)
            printed_output = mock_stdout.getvalue().strip()
            self.assertEqual(expected_output, printed_output)

    def test_display_nonexistent_directory(self):
        # Test displaying a directory that does not exist
        directory_name = "/nonexistent_directory"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.display_directory_content(directory_name)
            self.assertFalse(result)
            printed_output = mock_stdout.getvalue().strip()
            self.assertIn(f"{ErrorMessages.NotFoundError.value}", printed_output)  # Check if it prints an error message

    def test_copy_existing_dir_to_existing_dir_recursive(self):
        # Test copying from an existing directory to another existing directory recursively
        source_dir_path = "/source_dir"
        destination_dir_path = "/destination_dir"
        # Create source and destination directories
        self.file_system_manager.create_file_or_dir(source_dir_path, file=False)
        self.file_system_manager.create_file_or_dir(destination_dir_path, file=False)
        # Create some children in the source directory
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1", file=False)
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child2", file=True, content="hi")
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1" + "/child3", file=True, content="hi")
        # Copy the source directory to the destination recursively and ensure the copy operation was successful
        result = self.file_system_manager.copy_file_or_dir(source_dir_path, destination_dir_path, recursive=True)
        self.assertTrue(result)
        # Retrieve the source and destination directory nodes
        source_node = self.file_system_manager.path_handler.get_node_by_path(source_dir_path)
        parent_dir_path, source_dir_name = self.file_system_manager.path_handler.split_path(source_dir_path)
        destination_node = self.file_system_manager.path_handler.get_node_by_path(f"{destination_dir_path}/{source_dir_name}")
        # Check if the names, sizes, and the number of children match
        self.assertEqual(source_node.name, destination_node.name)
        self.assertEqual(source_node.size, destination_node.size)
        self.assertEqual(len(source_node.children), len(destination_node.children))

    def test_copy_existing_dir_to_existing_dir_non_recursive(self):
        # Test copying from an existing directory to another existing directory non-recursively
        source_dir_path = "/source_dir"
        destination_dir_path = "/destination_dir"
        # Create source and destination directories
        self.file_system_manager.create_file_or_dir(source_dir_path, file=False)
        self.file_system_manager.create_file_or_dir(destination_dir_path, file=False)
        # Create some children in the source directory for testing
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1", file=False)
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child2", file=True, content="hi")
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1" + "/child3", file=True, content="hi")
        # Copy the source directory to the destination non-recursively and Ensure the copy operation was successful
        result = self.file_system_manager.copy_file_or_dir(source_dir_path, destination_dir_path, recursive=False)
        self.assertTrue(result)
        # Retrieve the source and destination directory nodes
        source_node = self.file_system_manager.path_handler.get_node_by_path(source_dir_path)
        parent_dir_path, source_dir_name = self.file_system_manager.path_handler.split_path(source_dir_path)
        destination_node = self.file_system_manager.path_handler.get_node_by_path(
            f"{destination_dir_path}/{source_dir_name}")

        # Check if the names and the number of children match. the sizes should not match (it's not recursively)
        self.assertEqual(source_node.name, destination_node.name)
        self.assertEqual(len(source_node.children), len(destination_node.children))
        self.assertNotEqual(source_node.size, destination_node.size)

    def test_copy_existing_dir_to_non_existing_dir_recursive(self):
        # Test copying from an existing directory to a non-existing directory recursively
        source_dir_path = "/source_dir"
        destination_dir_path = "/non_existing_dir"
        # Create source directory
        self.file_system_manager.create_file_or_dir(source_dir_path, file=False)
        # Create some children in the source directory for testing
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1", file=False)
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child2", file=True, content="hi")
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1" + "/child3", file=True, content="hi")
        # Copy the source directory to the non-existing destination recursively and ensure the copy operation was successful
        result = self.file_system_manager.copy_file_or_dir(source_dir_path, destination_dir_path, recursive=True)
        self.assertTrue(result)
        # Retrieve the source and destination directory nodes
        source_node = self.file_system_manager.path_handler.get_node_by_path(source_dir_path)
        parent_dir_path, source_dir_name = self.file_system_manager.path_handler.split_path(source_dir_path)
        destination_node = self.file_system_manager.path_handler.get_node_by_path(
            f"{destination_dir_path}/{source_dir_name}")
        # Check if the names, sizes, and the number of children match
        self.assertEqual(source_node.name, destination_node.name)
        self.assertEqual(source_node.size, destination_node.size)
        self.assertEqual(len(source_node.children), len(destination_node.children))

    def test_copy_existing_dir_to_non_existing_dir_non_recursive(self):
        # Test copying from an existing directory to a non-existing directory non-recursively
        source_dir_path = "/source_dir"
        destination_dir_path = "/non_existing_dir"
        # Create source directory
        self.file_system_manager.create_file_or_dir(source_dir_path, file=False)
        # Create some children in the source directory for testing
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1", file=False)
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child2", file=True, content="hi")
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1/child3", file=True, content="hi")
        # Copy the source directory to the non-existing destination non-recursively
        result = self.file_system_manager.copy_file_or_dir(source_dir_path, destination_dir_path, recursive=False)
        self.assertTrue(result)
        # Retrieve the source and destination directory nodes
        source_node = self.file_system_manager.path_handler.get_node_by_path(source_dir_path)
        parent_dir_path, source_dir_name = self.file_system_manager.path_handler.split_path(source_dir_path)
        destination_node = self.file_system_manager.path_handler.get_node_by_path(
            f"{destination_dir_path}/{source_dir_name}")
        # Check if the names and the number of children match. the sizes should not match (it's not recursively)
        self.assertEqual(source_node.name, destination_node.name)
        self.assertEqual(len(source_node.children), len(destination_node.children))
        self.assertNotEqual(source_node.size, destination_node.size)

    def test_copy_non_existing_dir(self):
        # Test copying from a non-existing directory
        source_dir_path = "/non_existing_dir"
        destination_dir_path = "/destination_dir"
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.copy_file_or_dir(source_dir_path, destination_dir_path)
            # Verify that the result is False, indicating failure
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(ErrorMessages.InvalidPath.value, printed_message)

    def test_copy_existing_dir_to_file(self):
        # Test coping from an existing directory to a file (should return False)
        source_dir_path = "/non_existing_dir"
        destination_file_path = "/destination_dir"
        self.file_system_manager.create_file_or_dir(source_dir_path, file=False)
        self.file_system_manager.create_file_or_dir(destination_file_path, file=True)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.copy_file_or_dir(source_dir_path, destination_file_path)
            # Verify that the result is False, indicating failure
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(ErrorMessages.InvalidPath.value, printed_message)

    def test_copy_existing_file_to_non_existing_file(self):
        # Test copying from an existing file to a non-existing file
        source_file_path = "/source_file.txt"
        destination_file_path = "/non_existing_file.txt"
        self.file_system_manager.create_file_or_dir(source_file_path, file=True)

        result = self.file_system_manager.copy_file_or_dir(source_file_path, destination_file_path)
        # Verify that the result is True, indicating success
        self.assertTrue(result)
        # Assert that the destination file exists and its content matches the source file
        self.assertTrue(self.file_system_manager.path_handler.get_node_by_path(destination_file_path).is_file)
        self.assertEqual(self.file_system_manager.read_file(source_file_path, print_text=False),
                         self.file_system_manager.read_file(destination_file_path, print_text=False))

    def test_copy_existing_file_to_existing_file(self):
        # Test copying from an existing file to another existing file
        source_file_path = "/source_file.txt"
        destination_file_path = "/destination_file.txt"
        self.file_system_manager.create_file_or_dir(source_file_path, file=True)
        self.file_system_manager.create_file_or_dir(destination_file_path, file=True)

        result = self.file_system_manager.copy_file_or_dir(source_file_path, destination_file_path)
        # Verify that the result is True, indicating success
        self.assertTrue(result)
        # Assert that the destination file's content matches the source file
        self.assertEqual(self.file_system_manager.read_file(source_file_path, print_text=False),
                         self.file_system_manager.read_file(destination_file_path, print_text=False))

    def test_move_non_existing_source(self):
        # Test moving from a non-existing source path
        source_path = "/non_existing_source"
        destination_path = "/destination_dir"
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.move_file_or_dir(source_path, destination_path)
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(ErrorMessages.InvalidPath.value, printed_message)

    def test_move_existing_file_to_existing_file(self):
        # Test moving from an existing file to another existing file
        source_file_path = "/source_file.txt"
        destination_file_path = "/destination_file.txt"
        file_content = "text"
        self.file_system_manager.create_file_or_dir(source_file_path, file=True, content=file_content)
        self.file_system_manager.create_file_or_dir(destination_file_path, file=True)

        result = self.file_system_manager.move_file_or_dir(source_file_path, destination_file_path)
        self.assertTrue(result)
        # Verify that the source file has been deleted and that the destination file exist
        source_file_node = self.file_system_manager.path_handler.get_node_by_path(source_file_path, show_errors=False)
        self.assertFalse(source_file_node)
        destination_file_node = self.file_system_manager.path_handler.get_node_by_path(destination_file_path, show_errors=False)
        self.assertTrue(destination_file_node)
        # Assert that the destination file's content matches the source file
        self.assertEqual(file_content, self.file_system_manager.read_file(destination_file_path, print_text=False))

    def test_move_existing_file_to_existing_directory(self):
        # Test moving from an existing file to an existing directory
        source_file_path = "/source_file.txt"
        destination_dir_path = "/destination_dir"
        file_content = "text"
        self.file_system_manager.create_file_or_dir(source_file_path, file=True, content=file_content)
        self.file_system_manager.create_file_or_dir(destination_dir_path, file=False)

        result = self.file_system_manager.move_file_or_dir(source_file_path, destination_dir_path)
        self.assertTrue(result)
        # Verify that the source file has been deleted and that the destination directory now contains the source file
        source_file_node = self.file_system_manager.path_handler.get_node_by_path(source_file_path, show_errors=False)
        self.assertFalse(source_file_node)
        file_name = self.file_system_manager.path_handler.split_path(source_file_path)[1]
        destination_file_path = f"{destination_dir_path}/{file_name}" if destination_dir_path != "/" \
            else f"/{file_name}"
        destination_file_node = self.file_system_manager.path_handler.get_node_by_path(destination_file_path,
                                                                                       show_errors=False)
        self.assertTrue(destination_file_node)
        # Assert that the destination file's content matches the source file
        self.assertEqual(file_content, self.file_system_manager.read_file(destination_file_path, print_text=False))

    def test_move_existing_directory_to_file(self):
        # Test moving from an existing directory to a file (should return False)
        source_dir_path = "/source_dir"
        destination_file_path = "/destination_file.txt"
        self.file_system_manager.create_file_or_dir(source_dir_path, file=False)
        self.file_system_manager.create_file_or_dir(destination_file_path, file=True)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.move_file_or_dir(source_dir_path, destination_file_path)
            # Verify that the result is False, indicating failure
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(ErrorMessages.InvalidPath.value, printed_message)

    def test_move_existing_directory_to_existing_directory_recursive(self):
        # Test moving from an existing directory to another existing directory recursively
        source_dir_path = "/source_dir_to_move"
        destination_dir_path = "/destination_dir"
        # Create source and destination directories
        self.file_system_manager.create_file_or_dir(source_dir_path, file=False)
        self.file_system_manager.create_file_or_dir(destination_dir_path, file=False)
        # Create some children in the source directory
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1", file=False)
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child2", file=True, content="hi")
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1" + "/child3", file=True, content="hi")
        source_node = self.file_system_manager.path_handler.get_node_by_path(source_dir_path)
        excepted_name = source_node.name
        excepted_size = source_node.size
        excepted_children = len(source_node.children)
        # Move the source directory to the destination recursively and ensure the move operation was successful
        result = self.file_system_manager.move_file_or_dir(source_dir_path, destination_dir_path, recursive=True)
        self.assertTrue(result)
        # Retrieve the destination directory node and verify that the source deleted
        source_node = self.file_system_manager.path_handler.get_node_by_path(source_dir_path, show_errors=False)
        self.assertFalse(source_node)
        parent_dir_path, source_dir_name = self.file_system_manager.path_handler.split_path(source_dir_path)
        destination_node = self.file_system_manager.path_handler.get_node_by_path(f"{destination_dir_path}/{source_dir_name}")
        # Verify that the destination directory and its contents match the source
        self.assertEqual(excepted_name, destination_node.name)
        self.assertEqual(excepted_size, destination_node.size)
        self.assertEqual(excepted_children, len(destination_node.children))

    def test_move_existing_directory_to_existing_directory_non_recursive(self):
        # Test moving from an existing directory to another existing directory non-recursively
        source_dir_path = "/source_dir_to_move"
        destination_dir_path = "/destination_dir"
        # Create source and destination directories
        self.file_system_manager.create_file_or_dir(source_dir_path, file=False)
        self.file_system_manager.create_file_or_dir(destination_dir_path, file=False)
        # Create some children in the source directory
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1", file=False)
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child2", file=True, content="hi")
        self.file_system_manager.create_file_or_dir(source_dir_path + "/child1" + "/child3", file=True, content="hi")
        source_node = self.file_system_manager.path_handler.get_node_by_path(source_dir_path)
        excepted_name = source_node.name
        source_size = source_node.size
        excepted_children = len(source_node.children)
        # Move the source directory to the destination not recursively and ensure the move operation was successful
        result = self.file_system_manager.move_file_or_dir(source_dir_path, destination_dir_path, recursive=False)
        self.assertTrue(result)
        # Retrieve the destination directory node and verify that the source not deleted
        source_node = self.file_system_manager.path_handler.get_node_by_path(source_dir_path, show_errors=False)
        self.assertEqual(source_size, source_node.size)
        parent_dir_path, source_dir_name = self.file_system_manager.path_handler.split_path(source_dir_path)
        destination_node = self.file_system_manager.path_handler.get_node_by_path(f"{destination_dir_path}/{source_dir_name}")
        # Check if the names and the number of children match. the sizes should not match (it's not recursively)
        self.assertEqual(excepted_name, destination_node.name)
        self.assertNotEqual(source_size, destination_node.size)
        self.assertNotEqual(excepted_children, len(destination_node.children))
        self.assertEqual(0, len(destination_node.children))

    def test_search_no_results(self):
        # Test when no relevant files or directories are found
        self.file_system_manager.create_file_or_dir("/file1.txt", file=True, content="This is a sample file.")
        self.file_system_manager.create_file_or_dir("/dir1", file=False)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.search(search_name="nonexistent")   # search for a nonexistent file
            self.assertTrue(result)
            # Check the printed message to ensure no results were found
            printed_message = mock_stdout.getvalue().strip()
            self.assertEqual(printed_message, "Not found relevant file or directories")

    def test_search_with_results(self):
        # Test when files and directories are found based on search criteria
        self.file_system_manager.create_file_or_dir("/file1.txt", file=True, content="This is a sample file.")
        self.file_system_manager.create_file_or_dir("/file2.txt", file=True,
                                                    content="Another file with matching content.")
        self.file_system_manager.create_file_or_dir("/dir1", file=False)
        self.file_system_manager.create_file_or_dir("/dir2", file=False)

        # Check the printed message to verify that matching results are displayed
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            # Search with various criteria
            result = self.file_system_manager.search(search_content="matching content", file_extension=".txt",
                                                     min_size="0", start_path="/")
            self.assertTrue(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn("File results:", printed_message)
            self.assertNotIn("/file1.txt", printed_message)
            self.assertIn("/file2.txt", printed_message)
            self.assertNotIn("Directory results:", printed_message)
            self.assertNotIn("/dir1", printed_message)
            self.assertNotIn("/dir2", printed_message)

        # Search for a directory with a specific name
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.search(search_name="dir2", start_path="/")
            self.assertTrue(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertNotIn("File results:", printed_message)
            self.assertIn("Directory results:", printed_message)
            self.assertIn("/dir2", printed_message)

    def test_search_no_criteria_error(self):
        # Test when no search criteria are provided, expecting an error
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.search()
            self.assertFalse(result)
            # Check the printed message to verify that a specific error message is displayed
            printed_message = mock_stdout.getvalue().strip()
            self.assertEqual(printed_message, ErrorMessages.NoSearchCriteriaError.value)

    def test_search_invalid_min_size_error(self):
        # Test when an invalid min_size is provided
        for i in ["invalid", "-5"]:
            invalid_min_size = i
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = self.file_system_manager.search(min_size=invalid_min_size)
                self.assertFalse(result)
                # Check the printed message to verify that a specific error message is displayed
                printed_message = mock_stdout.getvalue().strip()
                self.assertEqual(printed_message, ErrorMessages.InvalidMinSizeError.value)

    def test_search_invalid_max_size_error(self):
        # Test when an invalid max_size is provided
        for i in ["invalid", "-5"]:
            invalid_max_size = i
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = self.file_system_manager.search(max_size=invalid_max_size)
                self.assertFalse(result)
                # Check the printed message to verify that a specific error message is displayed
                printed_message = mock_stdout.getvalue().strip()
                self.assertEqual(printed_message, ErrorMessages.InvalidMaxSizeError.value)

    def test_allocate_memory_buffer_max_file_size(self):
        # Test allocation error when reaching max file size
        file_name = "/max_size_file.txt"
        self.file_system_manager.create_file_or_dir(file_name, file=True)
        file_node = self.file_system_manager.path_handler.get_node_by_path(file_name)

        # Allocate memory until it exceeds the maximum file size
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            while self.file_system_manager.allocate_memory_buffer(file_node):
                pass
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            # Try allocating memory again for the same file
            result = self.file_system_manager.allocate_memory_buffer(file_node)
            # Check if the error message is printed
            self.assertFalse(result)
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(f"{ErrorMessages.ExceedsMaxMemoryFileError.value}{file_node.name}", printed_message)

    def test_allocate_memory_buffer_new_allocation_and_delete_memory_buffer_and_reuse_memory(self):
        # Test a new memory allocation, freeing the memory, and reusing available memory for allocation.
        file_name = "/new_allocation_file.txt"
        self.file_system_manager.create_file_or_dir(file_name, file=True)
        file_node = self.file_system_manager.path_handler.get_node_by_path(file_name)
        allocation_count = 4
        for i in range(allocation_count):
            # Allocate memory for the file
            result = self.file_system_manager.allocate_memory_buffer(file_node)
            self.assertTrue(result)
            file_allocation = file_node.file_memory_allocations
            self.assertEqual(len(file_allocation), i+1)
        old_file_allocation = file_node.file_memory_allocations.copy()
        # freeing the memory
        result = self.file_system_manager.delete_memory_buffer(file_node)
        self.assertTrue(result)
        # Verify that the memory has been freed and is available for future use
        for allocation in old_file_allocation:
            start_index, end_index, _ = allocation
            freed_memory = np.zeros(end_index - start_index)  # Create an array of zeros with the same size
            self.assertTrue(np.array_equal(self.file_system_manager.memory_buffer[start_index:end_index], freed_memory))
            self.assertIn(allocation[:-1], self.file_system_manager.allocation_available)
        old_allocation_available = self.file_system_manager.allocation_available.copy()
        for i in range(allocation_count):
            # Allocate memory for the file
            result = self.file_system_manager.allocate_memory_buffer(file_node)
            self.assertTrue(result)
            file_allocation = file_node.file_memory_allocations
            self.assertEqual(len(file_allocation), i+1)
            # Check if the newly allocated memory reuses available memory space
            self.assertIn(file_allocation[-1][:-1], old_allocation_available)

    def test_allocate_memory_buffer_max_buffer_expansion(self):
        # Test buffer expansion when allocation exceeds the buffer size
        file_name = "/max_buffer_size_file.txt"
        self.file_system_manager.create_file_or_dir(file_name, file=True)
        file_node = self.file_system_manager.path_handler.get_node_by_path(file_name)

        # Set the buffer size to a smaller value for testing
        new_buffer_size = DEFAULT_FILE_SIZE
        self.file_system_manager.memory_buffer = np.empty(dtype=np.int8, shape=(new_buffer_size,))
        self.file_system_manager.buffer_size = new_buffer_size
        self.file_system_manager.next_available_end_buffer_index = 0  # Track the current used length
        self.file_system_manager.allocation_available = []
        # Allocate memory once, this will consume the initial buffer size
        self.file_system_manager.allocate_memory_buffer(file_node)
        # Try allocating memory again for the same file, this should trigger buffer expansion
        result = self.file_system_manager.allocate_memory_buffer(file_node)
        self.assertTrue(result)
        # Check if the number of memory allocations matches the buffer size
        self.assertEqual(len(file_node.file_memory_allocations), self.file_system_manager.buffer_size/DEFAULT_FILE_SIZE)

    def test_allocate_memory_buffer_max_mem_size(self):
        # Test memory allocation error when exceeding max memory size
        file_name = "/max_mem_size_file.txt"  # Create a new file and retrieve its node
        self.file_system_manager.create_file_or_dir(file_name, file=True)
        file_node = self.file_system_manager.path_handler.get_node_by_path(file_name)

        # Set the buffer size to a maximum value for testing
        new_buffer_size = MAX_MEM_SIZE
        self.file_system_manager.memory_buffer = np.empty(dtype=np.int8, shape=(new_buffer_size))
        self.file_system_manager.buffer_size = new_buffer_size
        # Initialize the end buffer index to the maximum memory size (to simulate a fully utilized buffer)
        self.file_system_manager.next_available_end_buffer_index = MAX_MEM_SIZE
        self.file_system_manager.allocation_available = []

        # Try allocating memory again for the same file
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = self.file_system_manager.allocate_memory_buffer(file_node)
            # Check if the error message is printed and allocation is unsuccessful
            printed_message = mock_stdout.getvalue().strip()
            self.assertIn(ErrorMessages.ExceedsMaxSizeError.value, printed_message)
            self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
