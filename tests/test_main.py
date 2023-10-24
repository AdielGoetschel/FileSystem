import unittest
import io
import sys
from io import StringIO
from unittest.mock import patch
from main import main
from file_system_manager import FileSystemManager
from parser_command import Parser


class TestMainFunction(unittest.TestCase):

    def test_main(self):
        file_system_manager = FileSystemManager(check_for_backup_files=False)
        parser = Parser()
        test_inputs_and_outputs = {"create --name file0 --file True --content 'This is a test file.'": "",
                                   "size --name file0": str(len("This is a test file.")),
                                   "creation_time --name file0":
                                       lambda: file_system_manager.path_handler.get_node_by_path("file0").get_creation_time(),
                                   "last_modification_time --name file0":
                                       lambda: file_system_manager.path_handler.get_node_by_path("file0").get_last_modified(),
                                   "create --name /dir1/file1 --file True --recursive True --content "
                                   "'This is another test file.'": "",
                                   "create --name /dir2/file2 --file True --recursive True": "",
                                   "change_current_directory --name dir1": "",
                                   "go_to_previous_directory": "",
                                   "read --name /file0": "This is a test file.",
                                   "write --name file0 --append True --content ' And this is a new text.'": "",
                                   "read --name file0": "This is a test file." + " And this is a new text.",
                                   "create --name dir_to_del/file_to_del --recursive True": "",
                                   "delete --name dir_to_del": "",
                                   "search --search_name to_del": "Not found relevant file or directories",
                                   "copy --source_path dir1 --destination_path dir2 --recursive True": "",
                                   "search --search_name dir1 --start_path dir2": "dir2/dir1",
                                   "move --source_path file0 --destination_path dir2": "",
                                   "search --search_name file0 --start_path dir2": "dir2/file0",
                                   "quit": ""


        }

        for test_input, test_excepted_output in test_inputs_and_outputs.items():
            current_dir = file_system_manager.show_current_directory()
            # Create a StringIO to capture stdout
            output_stream = StringIO()
            # Use context manager to temporarily replace sys.stdout
            with unittest.mock.patch('sys.stdout', new=output_stream):
                # Simulate providing input to the function
                input_stream = StringIO(test_input + '\n')
                with unittest.mock.patch('sys.stdin', new=input_stream):
                    command_args, command_name = parser.get_input(current_dir)
                    command_function = file_system_manager.get_command_from_name(command_name)
                    result = command_function(**command_args)
            # If the test_output is a function, call it to get the actual value
            if callable(test_excepted_output):
                test_excepted_output = test_excepted_output()

            # Verify that the captured output equals/contains the expected output
            self.assertIn(test_excepted_output, output_stream.getvalue().replace("[/]$", "").strip())


if __name__ == "__main__":
    unittest.main()
