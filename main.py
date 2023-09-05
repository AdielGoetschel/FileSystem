from file_system_manager import FileSystemManager
from parser_command import Parser
from error_messages import ErrorMessages


def main():
    is_running: bool = True
    file_system_manager = FileSystemManager()
    parser = Parser()
    while is_running:
        current_dir = file_system_manager.show_current_directory()
        command_args, command_name = parser.get_input(current_dir)
        if command_args is None:
            continue
        # Get the function associated with the command
        command_function = file_system_manager.get_command_from_name(command_name)
        # Execute the command function with the parsed arguments
        result = command_function(**command_args)
        if result:
            print("Successfully..")
        else:
            print(ErrorMessages.GeneralError.value)


if __name__ == "__main__":
    main()
