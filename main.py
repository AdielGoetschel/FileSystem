import signal
import sys
from typing import List
from file_system_manager import FileSystemManager
from parser_command import Parser
from error_messages import ErrorMessages

is_running: bool = True  # Initialize a flag to control whether the program is running
STOP_EXECUTION_SIGNALS: List = [signal.SIGINT, signal.SIGTERM]  # Define a list of signals that can stop the program


def exit_type_signal_handler(signum, frame):
    global is_running
    is_running = False


# Register the signal handler for each signal in STOP_EXECUTION_SIGNALS
for sig in STOP_EXECUTION_SIGNALS:
    signal.signal(sig, exit_type_signal_handler)


def main():
    # Create instances of FileSystemManager and Parser
    file_system_manager = FileSystemManager()
    parser = Parser()

    while is_running:
        current_dir = file_system_manager.show_current_directory()
        try:
            # Get user input through the parser and retrieve command arguments and the command name
            command_args, command_name = parser.get_input(current_dir)
        except EOFError:
            print(f"did not receive user command...", file=sys.stderr)
            continue
        if command_args is None:
            continue
        if command_name == "quit":
            break
        # Get the function associated with the command
        command_function = file_system_manager.get_command_from_name(command_name)
        # Execute the command function with the parsed arguments
        result = command_function(**command_args)
        if result:
            if 'name' in command_args:
                print(f"{file_system_manager.get_success_message_from_name(command_name)}{command_args['name']}")
            elif 'source_path' in command_args and 'destination_path' in command_args:
                print(f"{file_system_manager.get_success_message_from_name(command_name)}{command_args['source_path']}"
                      f" to {command_args['destination_path']}")
            else:
                print(f"{file_system_manager.get_success_message_from_name(command_name)}")

        else:
            if 'name' in command_args:
                print(f"{file_system_manager.get_failure_message_from_name(command_name)}{command_args['name']}")
            elif 'source_path' in command_args and 'destination_path' in command_args:
                print(f"{file_system_manager.get_failure_message_from_name(command_name)}{command_args['source_path']}"
                      f" to {command_args['destination_path']}")
            else:
                print(f"{file_system_manager.get_failure_message_from_name(command_name)}")
        # print(file_system_manager.memory_buffer.tolist()[:50])

    # This block will always execute, ensuring create_backup is called
    while True:
        result = input("Create backup? (y/n) ").strip().lower()
        if result == 'y':
            backup_success = file_system_manager.create_backup()
            break
        elif result == 'n':
            break


if __name__ == "__main__":
    main()
