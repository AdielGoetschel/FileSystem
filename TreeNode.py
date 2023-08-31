import time
from datetime import datetime
from typing import Optional, Dict

"""
TreeNode represents a node in a file system hierarchy, capable of storing file or directory information.
It includes methods to manage and access properties such as content, permissions, and timestamps
"""


class TreeNode:
    def __init__(self, name: str, is_file: bool):
        self.name = name
        self.is_file = is_file
        self.children = []
        self.content: Optional[bytearray] = None
        if is_file:
            self.content = bytearray()  # Use bytearray to store the file content
            self.last_modified = time.time()  # Set current time as last modified time
            self.creation_time = time.time()
            self.permissions = {"read": True, "write": True}
        else:
            self.last_modified = None
            self.permissions = None

    @property
    def size(self) -> int:
        # Get the size of the content
        return len(self.content) if self.content is not None else 0

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
        # Remove a child node with the given name from the list of children
        self.children = []
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

    def write_content(self, data: str, mode: str = "w") -> None:
        """
        Write content to the node.

        Args:
            data (str): Content to be written.
            mode (str, optional): Write mode ('w' for overwrite, 'a' for append). Defaults to 'w'.
        """
        if self.is_file:
            if mode == "w":
                self.content = bytearray(data, "utf-8")  # Convert content to bytes using utf-8 encoding
            elif mode == "a":
                self.content += bytearray(data, "utf-8")
            self.last_modified = time.time()  # Update last modified time

    def read_content(self) -> str:
        # Read and retrieve content from the node
        if self.is_file:
            return bytes(self.content).decode("utf-8")  # Convert bytes to string using utf-8 encoding
