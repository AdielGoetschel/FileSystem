import unittest
from tree_node import TreeNode
from path_handler import PathHandler


class TestPathHandler(unittest.TestCase):
    def setUp(self):
        # Create an instance of the PathHandler class for testing
        self.path_handler = PathHandler(create_root=True)

    def test_is_absolute_path(self):
        # Test case for is_absolute_path method
        self.assertTrue(self.path_handler.is_absolute_path("/absolute/path"))
        self.assertFalse(self.path_handler.is_absolute_path("relative/path"))

    def test_split_path_absolute(self):
        # Test case for split_path method with an absolute path
        parent_dir, name = self.path_handler.split_path("/absolute/path/to/file.txt")
        self.assertEqual(parent_dir, "/absolute/path/to")
        self.assertEqual(name, "file.txt")

    def test_split_path_relative(self):
        # Test case for split_path method with a relative path
        # Set the current directory to a non-root directory
        self.path_handler.change_current_dir("/current/directory")
        parent_dir, name = self.path_handler.split_path("relative/path/to/file.txt")
        self.assertEqual(parent_dir, "/current/directory/relative/path/to")
        self.assertEqual(name, "file.txt")

    def test_get_node_by_path_existing(self):
        # Test case for get_node_by_path method with an existing path
        dir1_node = TreeNode("dir1", is_file=False, parent_node=self.path_handler.root)
        self.path_handler.root.add_child(dir1_node)
        file1_node = TreeNode("file1.txt", is_file=True, parent_node=dir1_node)
        dir1_node.add_child(file1_node)
        # Retrieve the nodes
        dir_node = self.path_handler.get_node_by_path("/dir1")
        file_node = self.path_handler.get_node_by_path("/dir1/file1.txt")
        self.assertIsNotNone(dir_node)
        self.assertIsNotNone(file_node)
        self.assertTrue(dir_node.is_file is False)
        self.assertTrue(file_node.is_file is True)

    def test_get_node_by_path_non_existing(self):
        # Test case for get_node_by_path method with a non-existing path
        node = self.path_handler.get_node_by_path("/non_existing/dir1/file.txt", show_errors=False)
        self.assertIs(node, False)

    def test_change_current_dir(self):
        # Test case for change_current_dir method
        # Change the current directory and check if it's updated
        self.path_handler.change_current_dir("/current/directory")
        self.assertEqual(self.path_handler.current_directory, "/current/directory")

    def test_go_back_dir(self):
        # Test case for go_back_dir method
        # Change the current directory, go back, and check if it's updated
        current_dir = self.path_handler.current_directory
        self.path_handler.change_current_dir("/new/directory")
        self.path_handler.go_back_dir()
        self.assertEqual(self.path_handler.current_directory, current_dir)


if __name__ == "__main__":
    unittest.main()