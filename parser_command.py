import argparse
import shlex
from typing import Union, Optional, Tuple, Dict
from file_system_manager import FileSystemManager
from error_messages import ErrorMessages


class Parser:
    def __init__(self):
        self.file_system_manager: FileSystemManager = FileSystemManager.instance()
        self.parser, self.subparsers = self.create_parser()

    # Function to create the argument parser with subparsers for commands
    def create_parser(self):
        # Create an ArgumentParser object for parsing command-line arguments
        parser = argparse.ArgumentParser(description="Command Line Interface")

        # Create subparsers to handle different commands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Loop through each command and its associated arguments in the command_mappings
        for command, (
                _, arg_names, mandatory_args, help_descriptor) in self.file_system_manager.command_mappings.items():
            # Add a subparser for the current command
            parser_command = subparsers.add_parser(command, help=self.file_system_manager.command_mappings[command][3][
                "command"])

            # Add command-specific arguments to the subparser
            for arg_name in arg_names:
                # Determine if the argument is mandatory based on the command's mandatory_args list
                required = arg_name in mandatory_args
                # Add the argument to the subparser with explanations
                if required:
                    parser_command.add_argument(f"--{arg_name}",
                                                help=self.file_system_manager.command_mappings[command][3][arg_name],
                                                required=required)
                else:
                    def_value = arg_names[arg_name]
                    parser_command.add_argument(f"--{arg_name}",
                                                help=self.file_system_manager.command_mappings[command][3][arg_name],
                                                required=required, default=def_value)

        return parser, subparsers

    def parse_command_string(self, input_string) -> Union[Optional[argparse.Namespace], str]:
        # Split the input string into a list of arguments
        args = shlex.split(input_string)

        if args[0] not in self.file_system_manager.command_mappings.keys():
            if args[0] == "help":
                self.parser.print_help()
                return None
            else:
                return args[0]

        # Check if the '--help' option is present in the arguments
        if '--help' in args[1:]:
            command_name = args[0]
            for action in self.parser._actions:
                if isinstance(action, argparse._SubParsersAction):  # Check if it's a subparsers action
                    if command_name in action.choices:
                        # Print the help_descriptor
                        print(self.file_system_manager.command_mappings[command_name][3]["command"])
                        action.choices[command_name].print_help()
            return None

        # parse the arguments
        return self.parser.parse_args(args)

    def get_input(self, current_dir: str) -> Union[Tuple[None, None], Tuple[Dict[str, Union[str, bool]], str]]:
        # The function gets the user input, parses the input string, and creates a dictionary of command arguments
        input_string = input(f"Current directory: {current_dir}\n" "Enter a command: ")  # Get user input for command

        if not input_string:
            return None, None

        # Parse the input string using parse_command_string
        args = self.parse_command_string(input_string)
        if args is None:  # Help message has been displayed, skip the command execution
            return None, None
        if not isinstance(args, argparse.Namespace):
            print(f"{ErrorMessages.InvalidCommandError.value}{args}")
            return None, None

        # Create a dictionary of command arguments from parsed arguments
        command_args = {
            arg_name: bool(arg_value.lower() == 'true') if arg_name in ["recursive", "add", "append"]
                                                           and isinstance(arg_value, str)
            else arg_value for arg_name, arg_value in vars(args).items() if arg_name != "command"}
        return command_args, args.command
