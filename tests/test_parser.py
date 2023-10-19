import unittest
from io import StringIO
from unittest.mock import patch
from file_system_manager import FileSystemManager
from parser_command import Parser


class TestParser(unittest.TestCase):
    def setUp(self):
        # Create an instance of the Parser class for testing
        self.file_system = FileSystemManager()
        self.parser = Parser()

    def test_parse_valid_command(self):
        # Test parsing a valid command with arguments
        input_string = "create --name myfile.txt --file true --content 'Hello, World!'"
        parsed_args = self.parser.parse_command_string(input_string)

        # Assert that the parsed arguments and command name match the expected values
        self.assertIsNotNone(parsed_args)
        self.assertEqual(parsed_args.command, "create")
        self.assertEqual(parsed_args.name, "myfile.txt")
        self.assertEqual(parsed_args.content, "Hello, World!")
        self.assertEqual(parsed_args.file, "true")

    @patch('sys.stderr', new_callable=StringIO)
    def test_create_missing_name_argument(self, mock_stderr):
        command = "create"  # Command name
        input_string = f"{command}"  # Missing the --name argument

        result = self.parser.parse_command_string(input_string)

        # Assert that the result is None, indicating an error
        self.assertIsNone(result)

        # Check if the expected error message is printed
        expected_error_message = "the following arguments are required: --name"
        self.assertIn(expected_error_message, mock_stderr.getvalue())

    def test_create_with_default_values(self):
        command = "create"  # Command name
        input_string = f"{command} --name my_file"  # Missing other arguments

        result = self.parser.parse_command_string(input_string)

        # Assert that the result is not None, indicating no error
        self.assertIsNotNone(result)

        # Check that default values are applied
        self.assertEqual(result.name, "my_file")
        self.assertEqual(result.file, False)
        self.assertEqual(result.content, "")
        self.assertEqual(result.recursive, False)

    @patch('sys.stdout', new_callable=StringIO)
    def test_parse_invalid_command(self, mock_stdout):
        # Test parsing an invalid command
        input_string = "invalid_command"
        parsed_args = self.parser.parse_command_string(input_string)

        # Assert that the parsed arguments are None
        self.assertIsNone(parsed_args)

        # Check if the expected error message is printed
        expected_error_message = f"Invalid Command: {input_string}"
        self.assertIn(expected_error_message, mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_help_for_command_option(self, mock_stdout):
        command = "create"
        input_string = f"{command} --help"  # Using the --help option
        result = self.parser.parse_command_string(input_string)

        # Assert that the result is None, indicating the help message is displayed
        self.assertIsNone(result)

        # Check if the expected help message is printed
        for arg in self.parser.file_system_manager.command_mappings["create"].arguments:
            self.assertIn(arg, mock_stdout.getvalue())
        expected_help_command_message = self.parser.file_system_manager.command_mappings["create"].help_info["command"]
        self.assertIn(expected_help_command_message, mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_parse_help_command(self, mock_stdout):
        # Test parsing the help command
        input_string = "help"
        parsed_args = self.parser.parse_command_string(input_string)

        # Assert that the parsed arguments are None
        self.assertIsNone(parsed_args)

        # Check if the expected help message is printed in stdout
        expected_help_message_1 = "Command Line Interface"
        self.assertIn(expected_help_message_1, mock_stdout.getvalue())
        expected_help_message_2 = "Available commands"
        self.assertIn(expected_help_message_2, mock_stdout.getvalue())



if __name__ == "__main__":
    unittest.main(buffer=False)
