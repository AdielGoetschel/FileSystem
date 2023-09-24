import math
import time
from datetime import datetime
from typing import Optional, Dict
import numpy as np
from error_messages import ErrorMessages

MEM_SIZE = 2 * 1024 * 1024
DEFAULT_FILE_SIZE = 10
MAX_FILE_SIZE = 100



"""
TreeNode represents a node in a file system hierarchy, capable of storing file or directory information.
It includes methods to manage and access properties such as content, permissions, and timestamps
"""


class TreeNode:
    def __init__(self, name: str, is_file: bool):
        self.name = name
        self.is_file = is_file
        if is_file:
            self.last_modified = time.time()  # Set current time as last modified time
            self.creation_time = time.time()
            self.permissions = {"read": True, "write": True}
            self.file_memory_allocations: list = []
        else:
            self.children: list = []

    @property
    def size(self) -> int:
        # Get the size of the content

        if self.is_file:
            if self.file_memory_allocations:
                # Check if the file has allocations
                size_content = 0 # Initialize

                for allocation in self.file_memory_allocations:
                    start_index, end_index, used_range = allocation
                    # Calculate the length of content in this allocation block
                    size_content += used_range
                return size_content
            else:
                return 0 # File not found in memory allocations

    def add_child(self, node: "TreeNode") -> None:
        # Add a child node to the given node
        self.children.append(node)

    def remove_child(self, child_name: str) -> bool:
        # Remove a child node with the given name from the list of children
        for child in self.children:
            if child.name == child_name:
                self.children.remove(child)
                return True
        return False

    def remove_all_children(self) -> bool:
        # Remove all children's
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
        # Get the last modification time of the node
        if self.is_file:
            return datetime.fromtimestamp(self.last_modified).strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_creation_time(self) -> Optional[str]:
        # Get the creation time of the node
        if self.is_file:
            return datetime.fromtimestamp(self.creation_time).strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_permissions(self) -> Optional[Dict[str, bool]]:
        #  Get the permissions of the node
        if self.is_file:
            return self.permissions
        return None


















