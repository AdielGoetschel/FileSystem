
from PathHandler import PathHandler
from TreeNode import TreeNode
from globals import ERRORS
from typing import Dict, List
"""
The FileSystemManager acts as a guide for users, helping them navigate and manipulate the file system
using the PathHandler for paths and the TreeNode for files and directories.
It streamlines tasks like creating, reading, writing, and organizing files, making file system management 
straightforward and user-friendly.
"""


class FileSystemManager:
    def __init__(self):
        self.path_handler = PathHandler()
        # dict of commands: in the list for each command:
        #     command function
        #     dict of all arguments(with default values if necessary)
        #     list of required arguments
        #     dict of help explanation of the command and the arguments
        self.command_mappings: Dict[str, List[callable, Dict[str], List[str], Dict[str, str]]] = {
            "create": [
                self.create_file_or_dir,
                {"name": "", "content": "", "recursive": False},
                ["name"],
                {
                    "command": "Create a new directory or file.",
                    "name": "Name of the directory or file to be created.",
                    "content": "(optional): Content to be written in the file.",
                    "recursive": "(optional): Create directories recursively (true/false)."
                }
            ],
            "read": [
                self.read_file,
                {"filename": ""},
                ["filename"],
                {
                    "command": "Read and display the content of a file.",
                    "filename": "Name of the file to be read."
                }
            ],
            "write": [
                self.write_to_file,
                {"filename": "", "content": "", "append": True},
                ["filename", "content"],
                {
                    "command": "Write content to a file.",
                    "filename": "Name of the file to write to.",
                    "content": "Content to be written.",
                    "append": "(optional): Append to the file (true/false)."
                }
            ],
            "delete": [
                self.delete_file_or_dir,
                {"name": ""},
                ["name"],
                {
                    "command": "Delete a file or directory.",
                    "name": "Name of the file or directory to be deleted."
                }
            ],
            "copy": [
                self.copy_file_or_dir,
                {'source_path': "", 'destination_path': "", 'recursive': False},
                ['source_path', 'destination_path'],
                {
                    "command": "Copy a file or directory to a new location.",
                    "source_path": "Path of the source file or directory.",
                    "destination_path": "Path of the destination directory.",
                    "recursive": "(optional): Copy recursively (true/false)."
                }
            ],
            "move": [
                self.move_file_or_dir,
                {"source_path": "", "destination_path": "", "recursive": False},
                ["source_path", "destination_path"],
                {
                    "command": "Move a file or directory to a new location.",
                    "source_path": "Path of the source file or directory.",
                    "destination_path": "Path of the destination directory.",
                    "recursive": "(optional): Move recursively (true/false)."
                }
            ],
            "list": [
                self.display_directory_content,
                {"directory_name": "", "recursive": False},
                ["directory_name"],
                {
                    "command": "List the content of a directory.",
                    "directory_name": "Name of the directory to list.",
                    "recursive": "(optional): List recursively (true/false)."
                }
            ],
            "size": [
                self.get_file_size,
                {"filename": ""},
                ["filename"],
                {
                    "command": "Get the size of a file in bytes.",
                    "filename": "Name of the file."
                }
            ],
            "permissions": [
                self.get_file_permissions,
                {"filename": ""},
                ["filename"],
                {
                    "command": "Get the permissions of a file.",
                    "filename": "Name of the file."
                }
            ],
            "set_permissions": [
                self.set_file_permissions,
                {"filename": "", "permission": "", "add": ""},
                ["filename", "permission", "add"],
                {
                    "command": "Set the permissions of a file.",
                    "filename": "Name of the file.",
                    "permission": "Permission to set.",
                    "add": "Add the permission (true/false)."
                }
            ],
            "creation_time": [
                self.get_creation_time,
                {"filename": ""},
                ["filename"],
                {
                    "command": "Get the creation time of a file.",
                    "filename": "Name of the file."
                }
            ],
            "last_modification_time": [
                self.get_last_modified_time,
                {"filename": ""},
                ["filename"],
                {
                    "command": "Get the last modification time of a file.",
                    "filename": "Name of the file."
                }
            ],
            "search": [
                self.search_files,
                {"search_filename": "", "search_content": "", "file_extension": "", "min_size": "", "max_size": "",
                 "start_path": "/"},
                ["search_filename"],
                {
                    "command": "Search for files matching specific criteria.",
                    "search_filename": "(optional): Search for files with a specific name.",
                    "search_content": "(optional): Search for files with specific content.",
                    "file_extension": "(optional): Search for files with a specific extension.",
                    "min_size": "(optional): Minimum size of files to search for.",
                    "max_size": "(optional): Maximum size of files to search for.",
                    "start_path": "(optional): Path to start the search from."
                }
            ],
            "change_current_directory": [
                self.update_current_dir,
                {"directory": ""},
                ["directory"],
                {
                    "command": "Change the current working directory.",
                    "directory": "Directory to change to."
                }
            ],
            "go_to_previous_directory": [
                self.go_to_previous_dir,
                [],
                {},
                {
                    "command": "Change the current working directory to the previous directory."
                }],
        }

    def _create_file_or_dir(self, new_name: str, parent_node: TreeNode, content: str = "") -> TreeNode:
        # Create a new directory or file node and add it as a child to the parent node
        is_file = self.path_handler.is_file(new_name)
        new_node = TreeNode(new_name, is_file)
        parent_node.add_child(new_node)
        if is_file and content:
            new_node.write_content(content)
        return new_node

    def create_file_or_dir(self, name: str, content: str = "", recursive: bool = False) -> bool:
        # Create a directory or a file with the given content
        parent_path, new_name = self.path_handler.split_path(name)
        parent_node = self.path_handler.get_node_by_path(parent_path, show_errors=False)
        if parent_node:
            if parent_node.is_file:  # the parent node should be a path, not a file
                print(f"{ERRORS['InvalidPath']}{name} The parent node should be a path, not a file")
                return False
            else:
                # Check if a node with the same name already exists in the parent directory
                existing_node = parent_node.get_child_by_name(new_name)
                if existing_node:
                    parent_path = "" if parent_path == "/" else parent_path
                    print(f"{parent_path}/{new_name}{ERRORS['ExistsError']}")
                    return False
                else:  # create the new node
                    self._create_file_or_dir(new_name, parent_node, content)
                    return True
        else:  # if the parent of the new node does not exist
            if not recursive:
                # The parent directory must exist for non-recursive creation
                print(f"{ERRORS['DirectoryNotFoundError']}{parent_path}")
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
                            new_node = self._create_file_or_dir(path_components[i], current_node, content)
                            return True
                        else:
                            if self.path_handler.is_file(path_components[i]):
                                # the parent node should be a path, not a file
                                print(
                                    f"{ERRORS['InvalidPath']}{name}. The parent node should be a path, not a file")
                                return False
                            else:
                                new_node = self._create_file_or_dir(path_components[i], current_node, content)
                                current_node = new_node
        return False

    def read_file(self, filename: str) -> bool:
        # Read and return the content of a file
        file_node = self.path_handler.get_node_by_path(filename, show_errors=True)
        if not file_node:
            return False
        if file_node.is_file:
            if file_node.get_permissions()["read"]:
                print(file_node.read_content())
                return True
            else:
                print(f"{ERRORS['ReadPermissionError']}")
                return False
        else:
            print(f"{ERRORS['IsADirectoryError']}Cannot read a directory")
            return False

    def write_to_file(self, filename: str, content: str, append: bool = True) -> bool:
        # Write content to a file
        file_node = self.path_handler.get_node_by_path(filename, show_errors=True)
        if not file_node:
            return False
        if file_node.is_file:
            if file_node.get_permissions()["write"]:
                if append:
                    file_node.write_content(content, mode="a")
                else:
                    file_node.write_content(content, mode="w")
                return True
            else:
                print(f"{ERRORS['WritePermissionError']}")
                return False
        else:
            print(f"{ERRORS['IsADirectoryError']}Cannot write to a directory")
            return False

    def delete_file_or_dir(self, name: str) -> bool:
        # Delete a file
        parent_dir_path, name_to_del = self.path_handler.split_path(name)
        parent_dir = self.path_handler.get_node_by_path(parent_dir_path, show_errors=True)
        if not parent_dir:
            return False
        else:
            if not parent_dir.is_file:
                result = parent_dir.remove_child(name_to_del)
                if result:
                    return True
                else:
                    if self.path_handler.is_file(name_to_del):
                        print(f"{ERRORS['FileNotFoundError']}{parent_dir_path}/{name_to_del}")
                    else:
                        print(f"{ERRORS['DirectoryNotFoundError']}{parent_dir_path}/{name_to_del}")
                    return False

            else:
                print(f"{ERRORS['InvalidPath']}{name}The parent node should be a path, not a file")
                return False

    def copy_file_or_dir(self, source_path: str, destination_path: str, recursive: bool = False) -> bool:
        source_dir_node = self.path_handler.get_node_by_path(source_path, show_errors=True)
        if not source_dir_node:
            return False
        if source_dir_node.is_file:
            # if source is a file - copy it
            if self.path_handler.is_file(destination_path):
                new_des_path = destination_path
            else:
                filename = self.path_handler.split_path(source_path)[1]
                new_des_path = f"{destination_path}/{filename}"
            des = self.path_handler.get_node_by_path(new_des_path, show_errors=False)
            if not des:  # if the destination file does not exist - create it
                return self.create_file_or_dir(new_des_path, content=source_dir_node.read_content(),
                                               recursive=True)
            else:  # if the destination file exist - write the content of the source file
                des.write_content(data=source_dir_node.read_content(), mode="w")
                return True

        else:  # if the source is a directory
            if not self.path_handler.is_file(destination_path):
                des = self.path_handler.get_node_by_path(destination_path, show_errors=False)
                if not des:  # if the destination directory does not exist - create it
                    result = self.create_file_or_dir(destination_path, recursive=True)
                    if not result:
                        return False
                if recursive:
                    # Copy files and directories recursively from the source to the destination if recursive is True
                    for child in source_dir_node.children:
                        child_source_path = f"{source_path}/{child.name}"
                        new_destination_path = f"{destination_path}/{child.name}"
                        result = self.copy_file_or_dir(child_source_path, new_destination_path, recursive=True)
                        if not result:
                            return False
                return True
            else:
                print(f"{ERRORS['InvalidPath']}{destination_path} the destination path should a directory format")
                return False

    def move_file_or_dir(self, source_path: str, destination_path: str, recursive: bool = False) -> bool:
        # Copy from source to destination
        copy_success = self.copy_file_or_dir(source_path, destination_path, recursive)
        if not copy_success:
            return False

        # Delete the original from the source
        if self.path_handler.is_file(source_path):  # delete the source file
            delete_success = self.delete_file_or_dir(source_path)
        else:  # delete the content of the source directory (and not the directory)
            source_node = self.path_handler.get_node_by_path(source_path, show_errors=False)
            delete_success = source_node.remove_all_children()
        return delete_success

    def display_directory_content(self, directory_name: str, recursive: bool = False, indent: int = 0) -> bool:
        # Display the content of a directory
        if directory_name == ".":
            dir_node = self.path_handler.get_node_by_path(self.path_handler.current_directory)
            directory_name = self.path_handler.current_directory
        else:
            dir_node = self.path_handler.get_node_by_path(directory_name, show_errors=True)
        if not dir_node:
            return False
        elif dir_node.is_file:
            print(f"{ERRORS['InvalidPath']}{directory_name} the path should a directory and not a file")
            return False
        else:
            print(f"{'    ' * indent}└── {dir_node.name}")
            for child in dir_node.children:
                if recursive and not child.is_file:
                    self.display_directory_content(f"{directory_name}/{child.name}", recursive=True, indent=indent + 1)
                else:
                    if child.is_file:
                        print(f"{'    ' * (indent + 1)}├── {child.name}")
                    else:
                        print(f"{'    ' * (indent + 1)}└── {child.name}")
            return True

    def get_file_size(self, filename: str) -> bool:
        # get the size of the file in bytes
        file_node = self.path_handler.get_node_by_path(filename, show_errors=True)
        if not file_node:
            return False
        elif file_node.is_file:
            print(file_node.size)
            return True
        else:
            print(f"{ERRORS['IsADirectoryError']}Cannot get size of a directory")
            return False

    def get_creation_time(self, filename: str) -> bool:
        # get the creation time of the file
        file_node = self.path_handler.get_node_by_path(filename, show_errors=True)
        if not file_node:
            return False
        elif file_node.is_file:
            print(file_node.get_creation_time())
            return True
        else:
            print(f"{ERRORS['IsADirectoryError']}Cannot get creation time of a directory")
            return False

    def get_last_modified_time(self, filename: str) -> bool:
        # get the last modification time of a file
        file_node = self.path_handler.get_node_by_path(filename, show_errors=True)
        if not file_node:
            return False
        elif file_node.is_file:
            print(file_node.get_last_modified())
            return True
        else:
            print(f"{ERRORS['IsADirectoryError']}Cannot get  last modification time of a directory")
            return False

    def get_file_permissions(self, filename: str) -> bool:
        # get the file permissions
        file_node = self.path_handler.get_node_by_path(filename, show_errors=True)
        if not file_node:
            return False
        elif file_node.is_file:
            permissions = ""
            for permission in file_node.get_permissions():
                permissions += f"{permission}: {file_node.get_permissions()[permission]}" + "\n"
            print(permissions)
            return True
        else:
            print(f"{ERRORS['IsADirectoryError']}Cannot get permissions of a directory")
            return False

    def set_file_permissions(self, filename: str, permission: str, add: bool) -> bool:
        # set the file permissions
        file_node = self.path_handler.get_node_by_path(filename, show_errors=True)
        if not file_node:
            return False
        elif file_node.is_file:
            file_node.get_permissions()[permission] = add
            return True
        else:
            print(f"{ERRORS['IsADirectoryError']}Cannot set permissions of a directory")
            return False

    def show_current_directory(self) -> str:
        # show current directory
        return self.path_handler.current_directory

    def update_current_dir(self, directory: str) -> bool:
        # change the current working directory
        if self.path_handler.is_file(directory):
            print(f"{ERRORS['InvalidPath']}{directory}"
                  f" The new current directory should be a path, not a file")
            return False
        exist_dir = self.path_handler.get_node_by_path(directory, show_errors=True)
        if not exist_dir:
            return False
        elif self.path_handler.is_absolute_path(directory):
            self.path_handler.change_current_dir(directory)
        else:
            self.path_handler.change_current_dir(f"{self.path_handler.current_directory}/{directory}")
        return True

    def go_to_previous_dir(self) -> bool:
        # change the current working directory to the previous directory
        return self.path_handler.go_back_dir()

    def search_files(self, search_filename: str = None, search_content: str = None, file_extension: str = None,
                     min_size: str = None, max_size: str = None, start_path: str = "/") -> bool:
        # Search for files matching specific criteria
        results = []

        def dfs_search(current_node: TreeNode, current_node_path: str) -> None:
            if current_node.is_file and (
                    (not file_extension or current_node.name.lower().endswith(file_extension.lower()))
                    and (not min_size or current_node.size >= int(min_size))
                    and (not max_size or current_node.size <= int(max_size))
                    and (not search_filename or search_filename.lower() in current_node.name.lower())
                    and (not search_content or search_content.lower() in current_node.read_content().lower())
            ):
                results.append(current_node_path)

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
        print(results)
        return True
