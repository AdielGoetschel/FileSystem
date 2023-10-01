import math
import os
from dataclasses import dataclass
from datetime import datetime

from path_handler import PathHandler
from tree_node import TreeNode
from error_messages import ErrorMessages
from typing import Dict, List, Union, Callable, Type, Optional
import numpy as np
import json
import time

MEM_SIZE = 2 * 1024 * 1024
MAX_MEM_SIZE = 4 * 2 * 1024 * 1024
DEFAULT_FILE_SIZE = 10
MAX_FILE_SIZE = 100

JSON_FILE = "filesystem.json"
NUMPY_FILE = "numpy_data.npy"
"""
The FileSystemManager simplifies file system operations.
It offers easy file and directory creation, modification, and deletion, along with features like searching for files. 
Users can also create and restore backups of the entire file system.
This user-centric tool streamlines file management for efficient and intuitive use.
"""


@dataclass
class CommandLayout:
    cb: Callable
    arguments: Dict[str, Union[str, bool]]
    required_arguments: List[str]
    help_info: Dict[str, str]
    success_message: str
    failure_message: str


CommandMappingType: Type[Dict[str, CommandLayout]]


class FileSystemManager:
    _instance = None

    def __new__(cls):
        # create a new instance of a class
        if cls._instance is None:
            # if the singleton instance has not been created, create a new instance of the class
            cls._instance = super(FileSystemManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls):
        # Return the existing singleton instance
        return cls._instance

    def __init__(self):
        if not os.path.exists(JSON_FILE) or not os.path.exists(NUMPY_FILE):
            self.path_handler: PathHandler = PathHandler(create_root=True)
            self.memory_buffer = np.empty(dtype=np.int8, shape=(MEM_SIZE,))
            self.buffer_size = MEM_SIZE
            self.next_available_end_buffer_index = 0  # Track the current used length
            self.allocation_available = []
        else:
            self.path_handler: PathHandler = PathHandler(create_root=False)
            self.restore_backup()

        """
        dict of commands: for each command, includes:
            - The command function
            - A dictionary of all arguments (with default values if necessary)
            - A list of required arguments
            - A dictionary of help explanations for the command and its arguments
            - A success message for the command 
            - A failure message for the command
        """
        self.command_mappings: CommandMappingType = {
            "create": CommandLayout(
                self.create_file_or_dir,
                {"name": "", "file": False, "content": "", "recursive": False},
                ["name"],
                {
                    "command": "Create a new directory or file.",
                    "name": "Name of the directory or file to be created.",
                    "content": "(optional): Content to be written in the file.",
                    "recursive": "(optional, default: False): Create directories recursively (true/false).",
                    "file": "(optional, default: False): Create file(true/false)."

                },
                "Successfully created ",
                "Failed to create "
            ),
            "read": CommandLayout(
                self.read_file,
                {"name": ""},
                ["name"],
                {
                    "command": "Read and display the content of a file.",
                    "name": "Name of the file to be read."
                },
                "Successfully read file ",
                "Failed to read file "

            ),
            "write": CommandLayout(
                self.write_to_file,
                {"name": "", "content": "", "append": True},
                ["name", "content"],
                {
                    "command": "Write content to a file.",
                    "name": "Name of the file to write to.",
                    "content": "Content to be written.",
                    "append": "(optional, default: True): Append to the file (true/false)."
                },
                "Successfully wrote to file ",
                "Failed to write to file "
            ),
            "delete": CommandLayout(
                self.delete_file_or_dir,
                {"name": ""},
                ["name"],
                {
                    "command": "Delete a file or directory.",
                    "name": "Name of the file or directory to be deleted."
                },
                "Successfully deleted ",
                "Failed to delete "

            ),
            "copy": CommandLayout(
                self.copy_file_or_dir,
                {'source_path': "", 'destination_path': "", 'recursive': False},
                ['source_path', 'destination_path'],
                {
                    "command": "Copy a file or directory to a new location.",
                    "source_path": "Path of the source file or directory.",
                    "destination_path": "Path of the destination directory.",
                    "recursive": "(optional, default: False): Copy recursively (true/false)."
                },
                "Successfully copied ",
                "Failed to copy "

            ),
            "move": CommandLayout(
                self.move_file_or_dir,
                {"source_path": "", "destination_path": "", "recursive": False},
                ["source_path", "destination_path"],
                {
                    "command": "Move a file or directory to a new location.",
                    "source_path": "Path of the source file or directory.",
                    "destination_path": "Path of the destination directory.",
                    "recursive": "(optional, default: False): Move recursively (true/false)."
                },
                "Successfully moved ",
                "Failed to move "
            ),
            "list": CommandLayout(
                self.display_directory_content,
                {"name": "", "recursive": False},
                ["name"],
                {
                    "command": "List the content of a directory.",
                    "name": "Name of the directory to list.",
                    "recursive": "(optional, default: False): List recursively (true/false)."
                },
                "Successfully listed contents of ",
                "Failed to list contents of ",

            ),
            "size": CommandLayout(
                self.get_size,
                {"name": ""},
                ["name"],
                {
                    "command": "Get the size in bytes.",
                    "name": "Name of the file/directory."
                },
                "Successfully retrieved size of ",
                "Failed to retrieve size of "
            ),
            "creation_time": CommandLayout(
                self.get_creation_time,
                {"name": ""},
                ["name"],
                {
                    "command": "Get the creation time.",
                    "name": "Name of the file/directory."
                },
                "Successfully retrieved creation time of ",
                "Failed to retrieve creation time of "
            ),
            "last_modification_time": CommandLayout(
                self.get_last_modified_time,
                {"name": ""},
                ["name"],
                {
                    "command": "Get the last modification time.",
                    "name": "Name of the file/directory."
                },
                "Successfully retrieved last modification time of ",
                "Failed to retrieve last modification time of "
            ),
            "search": CommandLayout(
                self.search,
                {"search_name": "", "search_content": "", "file_extension": "", "min_size": "", "max_size": "",
                 "start_path": "/"},
                [],
                {
                    "command": "Search for files and directories matching specific criteria.",
                    "search_name": "(optional): Search for files/directories with a specific name.",
                    "search_content": "(optional): Search for files with specific content.",
                    "file_extension": "(optional): Search for files with a specific extension.",
                    "min_size": "(optional): Minimum size of files to search for.",
                    "max_size": "(optional): Maximum size of files to search for.",
                    "start_path": "(optional): Path to start the search from."
                },
                "Search completed successfully",
                "Search failed"
            ),
            "change_current_directory": CommandLayout(
                self.update_current_dir,
                {"name": ""},
                ["name"],
                {
                    "command": "Change the current working directory.",
                    "name": "Directory to change to."
                },
                "Successfully changed to directory ",
                "Failed to change to directory "
            ),
            "go_to_previous_directory": CommandLayout(
                self.go_to_previous_dir,
                {},
                [],
                {
                    "command": "Change the current working directory to the previous directory."
                },
                "Successfully navigated to the previous directory",
                "Failed to navigate to the previous directory"
            ),
            "quit": CommandLayout(
                lambda: True,
                {},
                [],
                {
                    "command": "Quit the program."
                },
                "Successfully quit the program",
                "Failed to quit the program"
            ),
        }

    def get_command_from_name(self, command_name: str) -> callable:
        return self.command_mappings[command_name].cb

    def get_success_message_from_name(self, command_name: str) -> callable:
        return self.command_mappings[command_name].success_message

    def get_failure_message_from_name(self, command_name: str) -> callable:
        return self.command_mappings[command_name].failure_message



    def allocate_memory_buffer(self, file_node: TreeNode) -> bool:
        # Allocate memory for a file
        # Check if the file has reached the maximum allowed memory allocations
        if file_node.file_memory_allocations:
            count_allocations = len(file_node.file_memory_allocations)
            if count_allocations == MAX_FILE_SIZE // DEFAULT_FILE_SIZE:
                print(f"{ErrorMessages.ExceedsMaxMemoryFileError.value}{file_node.name}")
                return False
        # Check if there is available memory space
        if not self.allocation_available:
            # If there's no available space, calculate the start and end indexes for memory allocation
            start_index = self.next_available_end_buffer_index
            end_index = start_index + DEFAULT_FILE_SIZE
            # Check if the memory allocation exceeds the memory buffer size
            if end_index > self.buffer_size:
                if end_index > MAX_MEM_SIZE:
                    # If the allocation exceeds the maximum memory size, return an error message
                    print(ErrorMessages.ExceedsMaxSizeError.value)
                    return False
                else:
                    """
                    If the allocation smaller than the max buffer size allowed but exceeds the buffer size, 
                    expand the buffer by creating a new memory buffer with doubled size
                    """
                    new_memory_buffer = np.empty(dtype=np.int8, shape=(self.buffer_size * 2,))
                    new_memory_buffer[:self.buffer_size] = self.memory_buffer
                    self.memory_buffer = new_memory_buffer
            new_allocation = True
        else:
            # If there are available memory allocations, use the first one
            free_indexes = self.allocation_available.pop(0)
            start_index, end_index = free_indexes
            new_allocation = False

        # Add the memory allocation information to the file node
        file_node.file_memory_allocations.append([start_index, end_index, 0])
        if new_allocation:
            # Update the buffer index to point to the next available space in the buffer
            self.next_available_end_buffer_index += DEFAULT_FILE_SIZE
        return True

    def delete_memory_buffer(self, file_node: TreeNode) -> bool:
        """
        This method frees memory space previously allocated to a file and marks the allocated
        memory blocks as available for future use.
        """
        if not file_node.file_memory_allocations:
            # If there are no memory allocations for the file, return True (nothing to delete)
            return True
        else:
            while file_node.file_memory_allocations:
                # Iterate through the file's memory allocations and release the memory
                start_index, end_index, _ = file_node.file_memory_allocations.pop(0)
                # Set the memory block to 0 (freeing the memory)
                self.memory_buffer[start_index:end_index] = 0
                # Mark the released memory block as available for future use
                self.allocation_available.append([start_index, end_index])
            return True

    def update_parents(self, node_to_start_to_update:TreeNode, last_modification_time: float,
                       delta_size: Optional[int] = None):
        # Start updating parent nodes from the given node up to the root
        parent_node = node_to_start_to_update
        while parent_node is not None:
            # Update the last modification time of the current parent node
            parent_node.last_modified = last_modification_time
            # If delta_size is provided and not zero, update the size of the parent node
            if delta_size and delta_size != 0:
                parent_node.size += delta_size
            # Move to the next parent node (if any)
            parent_node = parent_node.parent_node


    def update_file_size(self, file_node: TreeNode) -> int:
        """
        Get the size of the content in the node.
        For files, it calculates the sum of memory allocations.
        """
        if file_node.is_file:
            if file_node.file_memory_allocations:
                size_content = 0  # Initialize

                for allocation in file_node.file_memory_allocations:
                    start_index, end_index, used_range = allocation
                    # Calculate the length of content in this allocation block
                    size_content += used_range
                file_node.size = size_content
                return size_content
            else:
                return 0  # File not found in memory allocations

    def _create_file_or_dir(self, new_name: str, parent_node: TreeNode, file: bool = False,
                            content: str = "") -> Union[bool, TreeNode]:
        # Create a new directory or file node and add it as a child to the parent node
        is_file = file
        new_node = TreeNode(new_name, is_file, parent_node)
        parent_node.add_child(new_node)
        if is_file and content:
            # If it's a file and content is provided, write the content to the file
            write_success = self.write_to_file(new_node, content, append=False)
            if not write_success:
                return False
        else:
            # If it's a directory or there's no content, update parent nodes' last_modified time
            last_modified_time = new_node.last_modified
            self.update_parents(node_to_start_to_update=parent_node, last_modification_time=last_modified_time)
        return new_node

    def create_file_or_dir(self, name: str, file: bool = False, content: str = "", recursive: bool = False) -> bool:
        # Create a directory or a file with the given content
        if content and not file:
            print(f"{ErrorMessages.IsADirectoryError.value}Cannot write to a directory")
            return False
        parent_path, new_name = self.path_handler.split_path(name)
        parent_node = self.path_handler.get_node_by_path(parent_path, show_errors=False)
        if parent_node:
            if parent_node.is_file:  # the parent node should be a path, not a file
                print(f"{ErrorMessages.InvalidPath.value}{name} The parent node should be a path, not a file")
                return False
            else:
                # Check if a node with the same name already exists in the parent directory
                existing_node = parent_node.get_child_by_name(new_name)
                if existing_node:
                    parent_path = "" if parent_path == "/" else parent_path
                    print(f"{parent_path}/{new_name}{ErrorMessages.ExistsError.value}")
                    return False
                else:  # create the new node
                    result = self._create_file_or_dir(new_name, parent_node, file=file, content=content)
                    if isinstance(result, TreeNode):
                        return True
                    else:
                        return False
        else:  # if the parent of the new node does not exist
            if not recursive:
                # The parent directory must exist for non-recursive creation
                print(f"{ErrorMessages.DirectoryNotFoundError.value}{parent_path}")
                return False

            else:  # handle case of recursive creation
                if name.startswith("/"):
                    current_node = self.path_handler.root
                else:
                    current_node = self.path_handler.get_node_by_path(self.path_handler.current_directory,
                                                                      show_errors=False)
                path_components = name.strip("/").split("/")
                for i in range(len(path_components)):
                    new_node = current_node.get_child_by_name(path_components[i])
                    if new_node:
                        current_node = new_node
                    else:
                        if i == len(path_components) - 1:
                            result = self._create_file_or_dir(path_components[i], current_node, file=file,
                                                              content=content)
                            if isinstance(result, TreeNode):
                                return True
                            else:
                                return False
                        else:
                            result = self._create_file_or_dir(path_components[i], current_node)
                            current_node = result
        return False

    def read_file(self, name: Union[TreeNode, str], print_text=True) -> Union[bool, str]:
        # Read and return the content of a file
        if isinstance(name, TreeNode):
            file_node = name
        else:
            file_node = self.path_handler.get_node_by_path(name, show_errors=True)
        if not file_node:
            return False
        if file_node.is_file:
            if file_node.file_memory_allocations:
                # Check if the file has allocations
                content = bytearray()  # Initialize an empty bytearray for the content
                for allocation in file_node.file_memory_allocations:
                    start_index, end_index, used_range = allocation
                    # Calculate the length of content in this allocation block
                    content_length = used_range
                    # Retrieve content from the memory buffer
                    content.extend(self.memory_buffer[start_index:start_index + content_length])
                # Decode the content from bytes to string using utf-8 encoding
                if print_text:
                    print(bytes(content).decode("utf-8"))
                    return True
                else:
                    return bytes(content).decode("utf-8")
            else:
                if print_text:
                    print("")
                    return True
                else:
                    return ""
        else:
            print(f"{ErrorMessages.IsADirectoryError.value}Cannot read a directory")
            return False

    def write_to_file(self, name: Union[TreeNode, str], content: str, append: bool = True) -> bool:
        # Write content to a file
        if isinstance(name, TreeNode):
            file_node = name
        else:
            file_node = self.path_handler.get_node_by_path(name, show_errors=True)
        if not file_node:
            return False
        if file_node.is_file:
            if not append:
                self.delete_memory_buffer(file_node)
            content_length = len(content)
            # Check if the file has an allocation, if not, allocate memory
            if not file_node.file_memory_allocations:
                allocation_success = self.allocate_memory_buffer(file_node)
                if not allocation_success:
                    return False
            # Retrieve the last allocated block's information
            last_allocated_ranges = file_node.file_memory_allocations[-1]
            start_index, end_index, used_range = last_allocated_ranges
            available_space = end_index - start_index - used_range
            new_start_index = start_index + used_range
            if content_length <= available_space:
                # Content fits within the available space
                self.memory_buffer[new_start_index:new_start_index + content_length] = bytearray(content,
                                                                                                 "utf-8")
                file_node.file_memory_allocations[-1] = [start_index, end_index,
                                                         used_range + content_length]
                # Update the last modification time of the file to the current time
                last_modified_time = time.time()
                file_node.last_modified = last_modified_time
                # Calculate the change in file size (delta) after writing the content
                old_file_size = file_node.size
                delta_file_size = self.update_file_size(file_node) - old_file_size
                # Update the modification times and sizes of parent directories
                # Starting from the parent node of the file
                self.update_parents(node_to_start_to_update=file_node.parent_node, last_modification_time=last_modified_time, delta_size=delta_file_size)
                return True
            else:
                if available_space > 0:
                    self.memory_buffer[new_start_index:new_start_index + available_space] = bytearray(
                        content[:available_space], "utf-8")
                    file_node.file_memory_allocations[-1] = [start_index, end_index,
                                                             used_range + available_space]
                    updated_content = content[available_space:]
                    content_length = len(updated_content)
                else:
                    updated_content = content
                new_blocks_count = math.ceil(content_length / DEFAULT_FILE_SIZE)
                for i in range(int(new_blocks_count)):
                    allocation_success = self.allocate_memory_buffer(file_node)
                    if not allocation_success:
                        return False
                    self.write_to_file(file_node, updated_content
                                       [DEFAULT_FILE_SIZE * i:DEFAULT_FILE_SIZE * (i + 1)], append=True)
                return True
        else:
            print(f"{ErrorMessages.IsADirectoryError.value}Cannot write to a directory")
            return False

    def delete_file_or_dir(self, name: str) -> bool:
        # Delete a file or a directory
        parent_dir_path, name_to_del = self.path_handler.split_path(name)
        parent_dir = self.path_handler.get_node_by_path(parent_dir_path, show_errors=True)
        node_to_del = self.path_handler.get_node_by_path(name, show_errors=True)
        if not parent_dir:
            # If the parent directory does not exist, cannot delete
            return False
        else:
            if not parent_dir.is_file:
                delta_size = 0
                if node_to_del.is_file:
                    # If the node to be deleted is a file, delete its memory buffer
                    old_file_size = node_to_del.size
                    self.delete_memory_buffer(node_to_del)
                    delta_size = -old_file_size if old_file_size !=0 else 0
                else:
                    # If the node to be deleted is a directory, recursively delete its contents
                    for child in node_to_del.children.copy():
                        child_path = f"{parent_dir_path}/{name_to_del}/{child.name}" if parent_dir_path != "/" \
                                    else f"/{name_to_del}/{child.name}"
                        # Recursively call delete_file_or_dir to delete each child node
                        self.delete_file_or_dir(child_path)
                # Remove the node to be deleted from the parent directory
                result = parent_dir.remove_child(name_to_del)
                if result:
                    last_modified_time = time.time()
                    # Check if delta_size is non-zero, indicating a change in size
                    if delta_size != 0:
                        # If delta_size is not zero, update the parent directory's size and last modification time
                        # and propagate the size change up the directory hierarchy
                        self.update_parents(node_to_start_to_update=parent_dir,
                                            last_modification_time=last_modified_time,
                                            delta_size=delta_size)
                    else:
                        # If delta_size is zero, only update the parent directory's
                        # last modification time without changing its size
                        self.update_parents(node_to_start_to_update=parent_dir,
                                            last_modification_time=last_modified_time)

                    return True
                else:
                    print(f"{ErrorMessages.DirectoryNotFoundError.value}{parent_dir_path}/{name_to_del}")
                    return False

            else:
                print(f"{ErrorMessages.InvalidPath.value}{name}The parent node should be a path, not a file")
                return False

    def copy_file_or_dir(self, source_path: str, destination_path: str, recursive: bool = False,
                         first_run: bool = True) -> bool:
        # Copy a file or directory from the source path to the destination path.
        source_dir_node = self.path_handler.get_node_by_path(source_path, show_errors=True)
        if not source_dir_node:
            # The source path does not exist, cannot copy
            print(f"ErrorMessages.InvalidPath.value{source_path}")
            return False
        if source_dir_node.is_file:
            # if source is a file - copy it
            destination_node = self.path_handler.get_node_by_path(destination_path, show_errors=False)
            if not destination_node:  # if the destination file does not exist - create it
                return self.create_file_or_dir(destination_path, file=True, content=self.read_file(source_dir_node,
                                                                                                   print_text=False),
                                               recursive=True)
            else:
                if destination_node.is_file:  # if the destination file exist - write the content of the source file
                    return self.write_to_file(destination_node, content=self.read_file(source_dir_node,
                                                                                       print_text=False), append=False)
                else:  # if the destination directory exist - create the file on this directory
                    filename = self.path_handler.split_path(source_path)[1]
                    new_des_path = f"{destination_path}/{filename}" if destination_path != "/" \
                        else f"/{destination_path}"
                    return self.create_file_or_dir(new_des_path, file=True,
                                                   content=self.read_file(source_dir_node, print_text=False),
                                                   recursive=True)

        else:  # if the source is a directory
            destination_node = self.path_handler.get_node_by_path(destination_path, show_errors=False)
            if isinstance(destination_node, TreeNode):
                # Ensure the destination is not a file (directories should be copied to directories)
                if destination_node.is_file:
                    print(f"{ErrorMessages.InvalidPath.value}{destination_path} "
                          f"the destination path should a directory format")
                    return False
            else:
                # if the destination directory does not exist - create it
                result = self.create_file_or_dir(destination_path, file=False, recursive=True)
                if not result:
                    return False
            if first_run:
                # On the first run, create a new directory at the destination
                copy_dir_name = self.path_handler.split_path(source_path)[1]
                new_des_copy_path = f"{destination_path}/{copy_dir_name}" if destination_path != "/" \
                    else f"/{copy_dir_name}"
                new_des_copy_node = self.create_file_or_dir(new_des_copy_path, file=False)
            else:
                new_des_copy_path = destination_path
            # Copy files and directories recursively from the source to the destination if recursive is True
            for child in source_dir_node.children:
                child_source_node = source_dir_node.get_child_by_name(child.name)
                child_source_path = f"{source_path}/{child.name}" if source_path != "/" \
                                    else f"/{child.name}"
                new_destination_path = f"{new_des_copy_path}/{child.name}" if destination_path != "/" \
                                       else f"/{child.name}"
                if child_source_node.is_file:
                    result = self.copy_file_or_dir(child_source_path, new_destination_path, recursive=True)
                else:
                    if not recursive:
                        result = self.create_file_or_dir(new_destination_path, file=False)
                    else:
                        result = self.copy_file_or_dir(child_source_path, new_destination_path, recursive=True,
                                                       first_run=False)

                if not result:
                    return False
            return True

    def move_file_or_dir(self, source_path: str, destination_path: str, recursive: bool = False) -> bool:
        # Move a file or directory from the source path to the destination path.
        source_dir_node = self.path_handler.get_node_by_path(source_path, show_errors=True)
        if not source_dir_node:
            # The source path does not exist, cannot move
            print(f"ErrorMessages.InvalidPath.value{source_path}")
            return False
        if source_dir_node.is_file:
            # If the source is a file, handle moving it
            old_parent_node = self.path_handler.get_node_by_path(self.path_handler.split_path(source_path)[0])
            destination_node = self.path_handler.get_node_by_path(destination_path, show_errors=False)
            if isinstance(destination_node, TreeNode) and destination_node.is_file:
                # If the destination is an existing file, overwrite it with the content of the source file
                # and delete the source file
                self.write_to_file(destination_node, content=self.read_file(source_dir_node, print_text=False),
                                   append=False)
                return self.delete_file_or_dir(source_path)
            else:
                # If the destination is an existing directory or a new directory
                if not isinstance(destination_node, TreeNode):
                    # If the destination directory does not exist, create it
                    self.create_file_or_dir(destination_path, file=False, recursive=True)
                # Get the new parent node for the source node (the destination directory)
                new_parent_node = self.path_handler.get_node_by_path(destination_path)
                # Move the source node to the destination
                new_parent_node.add_child(source_dir_node)
                source_dir_node.parent_node = new_parent_node
                old_parent_node.remove_child(source_dir_node.name)
                # Update the last modified time and sizes of the affected nodes
                last_modified_time = time.time()
                self.update_parents(node_to_start_to_update=old_parent_node, last_modification_time=last_modified_time,
                                    delta_size=-source_dir_node.size if source_dir_node.size != 0 else 0)
                self.update_parents(node_to_start_to_update=new_parent_node, last_modification_time=last_modified_time,
                                    delta_size=source_dir_node.size if source_dir_node.size != 0 else 0)
                return True

        else:  # if the source is a directory
            destination_node = self.path_handler.get_node_by_path(destination_path, show_errors=False)
            if isinstance(destination_node, TreeNode):
                if destination_node.is_file:
                    print(f"{ErrorMessages.InvalidPath.value}{destination_path} "
                          f"the destination path should a directory format")
                    return False
                else:
                    print(f"{source_path}{ErrorMessages.ExistsError.value}")
                    return False
            else:
                # if the destination directory does not exist, create it
                self.create_file_or_dir(destination_path, file=False, recursive=True)
                destination_node = self.path_handler.get_node_by_path(destination_path, show_errors=False)
            source_parent_path, source_dir_name = self.path_handler.split_path(source_path)
            if recursive:
                # Handle recursive move
                old_parent_node = self.path_handler.get_node_by_path(source_parent_path)
                dir_to_move = old_parent_node.get_child_by_name(source_dir_name)
                # Add the directory to the destination
                destination_node.add_child(dir_to_move)
                old_parent_node.remove_child(source_dir_name)
                dir_to_move.parent_node = destination_node
                # Update last modified time and sizes for affected nodes
                last_modified_time = time.time()
                self.update_parents(node_to_start_to_update=old_parent_node, last_modification_time=last_modified_time,
                                    delta_size=-dir_to_move.size if dir_to_move.size != 0 else 0)
                self.update_parents(node_to_start_to_update=destination_node, last_modification_time=last_modified_time,
                                    delta_size=dir_to_move.size if dir_to_move.size != 0 else 0)
            else:
                # Handle non-recursive move
                # Create a new directory in the destination with the same name as the source directory
                self.create_file_or_dir(name=f"{destination_path}/{source_dir_name}", file=False)
            return True

    def display_directory_content(self, name: str, recursive: bool = False, indent: int = 0) -> bool:
        # Display the content of a directory
        if name == ".":
            # If the name is ".", it represents the current directory.
            dir_node = self.path_handler.get_node_by_path(self.path_handler.current_directory)
            name = self.path_handler.current_directory
        else:
            # Get the directory node by the specified name/path.
            dir_node = self.path_handler.get_node_by_path(name, show_errors=True)
        if not dir_node:
            # If the directory node doesn't exist, return False.
            return False
        elif dir_node.is_file:
            # If it's a file, print an error message and return False.
            print(f"{ErrorMessages.InvalidPath.value}{name} the path should a directory and not a file")
            return False
        else:
            print(f"{'    ' * indent}└── {dir_node.name}")
            for child in dir_node.children:
                if recursive and not child.is_file:
                    # If recursive is True and the child is a directory, recursively display its content.
                    self.display_directory_content(f"{name}/{child.name}", recursive=True, indent=indent + 1)
                else:
                    if child.is_file:
                        print(f"{'    ' * (indent + 1)}├── {child.name}")
                    else:
                        print(f"{'    ' * (indent + 1)}└── {child.name}")
            return True

    def get_size(self, name: str) -> bool:
        # Get the size of in bytes
        node = self.path_handler.get_node_by_path(name, show_errors=True)
        if not node:  # Check if the node exists
            return False
        print(node.size)
        return True


    def get_creation_time(self, name: str) -> bool:
        # Get the creation time
        node = self.path_handler.get_node_by_path(name, show_errors=True)
        if not node:  # Check if the node exists
            return False
        print(node.get_creation_time())
        return True

    def get_last_modified_time(self, name: str) -> bool:
        # Get the last modification time
        node = self.path_handler.get_node_by_path(name, show_errors=True)
        if not node:  # Check if node exists
            return False
        print(node.get_last_modified())
        return True


    def show_current_directory(self) -> str:
        # display current directory
        return self.path_handler.current_directory

    def update_current_dir(self, name: str) -> bool:
        # Change the current working directory
        exist_dir = self.path_handler.get_node_by_path(name, show_errors=True)
        # Check if the new current directory exists
        if not isinstance(exist_dir, TreeNode):
            print(f"{ErrorMessages.DirectoryNotFoundError}{name}")
            return False
        elif exist_dir.is_file:
            print(f"{ErrorMessages.InvalidPath.value}{name}"
                  f" The new current directory should be a path, not a file")
            return False
        elif self.path_handler.is_absolute_path(name):
            self.path_handler.change_current_dir(name)
        else:
            self.path_handler.change_current_dir(f"{self.path_handler.current_directory}/{name}")
        return True

    def go_to_previous_dir(self) -> bool:
        # Change the current working directory to the previous directory
        return self.path_handler.go_back_dir()

    def output_search(self, file_results: List, directory_results: List) -> None:
        # Output search results
        if not file_results and not directory_results:
            # If no results were found, print a message
            print("Not found relevant file or directories")
        if file_results:
            # If there are search results, print each result
            print("File results:")
            for item in file_results:
                print(item)
        if directory_results:
            # If there are search results, print each result
            print("Directory results:")
            for item in directory_results:
                print(item)

    @staticmethod
    def is_positive_or_zero_integer(value):
        # Check if a value is a positive or zero integer
        try:
            if not value.isdigit():
                return False

            int_value = int(value)
            return int_value >= 0
        except ValueError:
            return False

    def search(self, search_name: str = None, search_content: str = None, file_extension: str = None,
               min_size: str = None, max_size: str = None, start_path: str = "/") -> bool:
        # Search for files matching specific criteria
        file_results = []
        directory_results = []
        # Check if at least one search parameter is given
        if all(param in [None, ""] for param in (search_name, search_content, file_extension, min_size, max_size)):
            print(ErrorMessages.NoSearchCriteriaError.value)
            return False
        # Check and validate min_size and max_size
        if min_size:
            if not self.is_positive_or_zero_integer(min_size):
                print(ErrorMessages.InvalidMinSizeError.value)
                return False
        if max_size:
            if not self.is_positive_or_zero_integer(max_size):
                print(ErrorMessages.InvalidMaxSizeError.value)
                return False

        def dfs_search(current_node: TreeNode, current_node_path: str) -> None:
            # Depth search for matching files and directories
            if current_node.is_file and (
                    (not file_extension or current_node.name.lower().endswith(file_extension.lower()))
                    and (not min_size or current_node.size >= int(min_size))
                    and (not max_size or current_node.size <= int(max_size))
                    and (not search_name or search_name.lower() in current_node.name.lower())
                    and (not search_content or search_content.lower() in self.read_file(current_node,
                                                                                        print_text=False).lower())
            ):
                file_results.append(current_node_path)
            elif not current_node.is_file and (search_name and search_name.lower() in current_node.name.lower()):
                directory_results.append(current_node_path)

            if not current_node.is_file:
                for child in current_node.children:
                    if current_node_path == "/":
                        child_path = "/" + child.name
                    else:
                        child_path = current_node_path + "/" + child.name
                    dfs_search(child, child_path)

        search_node = self.path_handler.get_node_by_path(start_path, show_errors=True)
        if not search_node:
            return False
        dfs_search(search_node, start_path)
        self.output_search(file_results, directory_results)
        return True

    def recursive_tree_to_dict(self, node: TreeNode) -> dict:
        # Convert the TreeNode hierarchy to a dictionary
        node_dict = {
            "name": node.name,
            "is_file": node.is_file,
            "parent_node": node.parent_node,
            "last_modified": node.last_modified,
            "creation_time": node.last_modified,
            "size": node.size
        }
        if node.is_file:
            node_dict["file_memory_allocations"] = node.file_memory_allocations
        else:
            node_dict["children"] = [self.recursive_tree_to_dict(child) for child in node.children]
        return node_dict

    def tree_to_dict(self, node: TreeNode):
        # Create a dictionary to represent the entire tree, including general metadata
        tree_dict = {
            "metadata": {"buffer_size": self.buffer_size,
                         "next_available_end_buffer_index": self.next_available_end_buffer_index,
                         "allocation_available": self.allocation_available},
            "root": self.recursive_tree_to_dict(node)
        }
        return tree_dict

    def create_backup(self) -> bool:
        filesystem_dict = self.tree_to_dict(self.path_handler.root)
        # Serialize the dictionary to JSON and save it to a file
        try:
            with open(JSON_FILE, "w") as json_file:
                json.dump(filesystem_dict, json_file, indent=4)
            # Save the NumPy array to a file
            np.save(NUMPY_FILE, self.memory_buffer)
            return True
        except Exception as e:
            print(f"Backup creation failed: {e}")
            return False

    def recursive_dict_to_tree(self, node_dict: Dict):
        # Recursively build a TreeNode hierarchy from a dictionary
        if not node_dict:
            return None
        node = TreeNode(node_dict["name"], node_dict["is_file"], node_dict["parent_node"])
        if node_dict["name"] == "/":
            self.path_handler.root = node
        node.last_modified = node_dict.get("last_modified")
        node.creation_time = node_dict.get("creation_time")
        node.size = node_dict.get("size")
        if node_dict["is_file"]:
            node.file_memory_allocations = node_dict.get("file_memory_allocations")
        else:
            node.children = [self. recursive_dict_to_tree(child_dict) for child_dict in node_dict.get("children", [])]
        return node

    def dict_to_tree(self, tree_dict: Dict):
        # Create a TreeNode hierarchy and metadata from a dictionary
        if not tree_dict or "root" not in tree_dict:
            return None
        root_dict = tree_dict["root"]
        metadata_dict = tree_dict["metadata"]
        self.buffer_size = metadata_dict["buffer_size"]
        self.next_available_end_buffer_index = metadata_dict["next_available_end_buffer_index"]
        self.allocation_available = metadata_dict["allocation_available"]
        self.recursive_dict_to_tree(root_dict)

    def restore_backup(self):
        # Load the JSON data from the file
        with open(JSON_FILE, "r") as json_file:
            filesystem_dict = json.load(json_file)
        # Create the root node and other nodes from the loaded data and the metadata
        self.dict_to_tree(filesystem_dict)

        # Load the NumPy array from the file
        self.memory_buffer = np.load(NUMPY_FILE)
