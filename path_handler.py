from tree_node import TreeNode
from error_messages import ErrorMessages
from typing import Union

"""
PathHandler manages file system paths.
"""


class PathHandler:
    def __init__(self, create_root=True):
        if create_root:
            self.root = TreeNode("/", is_file=False, parent_node=None)  # Create the root directory
        self.current_directory = "/"
        self.previous_directory = None

    def is_absolute_path(self, path: str) -> bool:
        # Check if he given path is an absolute path (starts with the root directory separator character ("/"))
        return path.startswith("/")

    def split_path(self, path: str) -> tuple:
        #  Split the given path into parent directory and name
        if self.is_absolute_path(path):
            # Check if the path is absolute
            parent_dir_path, _, file_or_dir_name = path.rpartition("/")
            if not parent_dir_path:  # If parent_dir_path is empty, set it to "/"
                parent_dir_path = "/"
        else:  # Relative path
            current_dir = self.current_directory  # Get the current working directory name
            path_components = path.strip("/").split("/")
            if current_dir == "/":
                parent_dir_path = "/" + "/".join(path_components[:-1])
            else:
                parent_dir_path = current_dir + "/" + "/".join(path_components[:-1])
            file_or_dir_name = path_components[-1]
        return parent_dir_path, file_or_dir_name

    def get_node_by_path(self, path: str, show_errors: bool = True) -> Union[TreeNode, bool]:
        # Get the node corresponding to the given path
        if not path:
            return False
        elif path == "/":
            return self.root
        elif self.is_absolute_path(path):
            # Start searching from the root node
            current_node = self.root
        else:
            # Start searching from the current node
            current_node = self.get_node_by_path(self.current_directory)   # start to search from the current node
        path_components = path.strip("/").split("/")
        for component in path_components:
            next_node = current_node.get_child_by_name(component)
            if not next_node:
                if show_errors:   # show error if the node is not found.
                    print(f"{ErrorMessages.DirectoryNotFoundError.value}{path}")
                return False
            current_node = next_node
        return current_node

    def change_current_dir(self, new_cur_directory: str) -> bool:
        # change the current working directory to the specified directory
        self.previous_directory = self.current_directory
        self.current_directory = new_cur_directory
        return True

    def go_back_dir(self) -> bool:
        # change the current working directory to the previous directory
        if not self.previous_directory:
            print(f"{ErrorMessages.DirectoryNotFoundError.value}previous directory does not found")
            return False
        cur_dir = self.current_directory
        self.current_directory = self.previous_directory
        self.previous_directory = cur_dir
        return True
