import time
from datetime import datetime
from typing import Optional, Dict, Union
MEM_SIZE = 2 * 1024 * 1024
DEFAULT_FILE_SIZE = 10
MAX_FILE_SIZE = 100

"""
TreeNode represents a node in a file system hierarchy, capable of storing file or directory information.
It includes methods to manage and access properties such as content, and timestamps
"""


class TreeNode:
    def __init__(self, name: str, is_file: bool, parent_node: Union['TreeNode', None]):
        self.name = name # Name of the node
        self.is_file = is_file # True if it's a file, False if it's a directory
        self.parent_node = parent_node
        self.creation_time = time.time()
        self.last_modified = time.time()  # Set current time as last modified time
        self.size = 0
        if is_file:
            # Initialize properties for files
            self.file_memory_allocations: list = []  # List to track memory allocations for files
        else:
            # Initialize properties for directories
            self.children: list = []  # List to store child nodes (subdirectories or files)

    def add_child(self, node: "TreeNode") -> None:
        # Add a child node (subdirectory or file) to the current node
        self.children.append(node)

    def remove_child(self, child_name: str) -> bool:
        # Remove a child node with the given name from the list of children
        for child in self.children:
            if child.name == child_name:
                self.children.remove(child)
                return True
        return False  # Child not found

    def remove_all_children(self) -> bool:
        # Remove all child nodes (subdirectories and files) from the current directory node.
        while self.children:
            self.children.pop()
        return True

    def get_child_by_name(self, name: str) -> Optional["TreeNode"]:
        # Get a child node by its name
        for child in self.children:
            if child.name == name:
                return child
        return None

    def get_last_modified(self) -> Optional[str]:
        # Get the last modification time of the node, Only applicable to files
        return datetime.fromtimestamp(self.last_modified).strftime("%Y-%m-%d %H:%M:%S")

    def get_creation_time(self) -> Optional[str]:
        # Get the creation time of the node,   Only applicable to files.
        return datetime.fromtimestamp(self.creation_time).strftime("%Y-%m-%d %H:%M:%S")


