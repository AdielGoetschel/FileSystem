import signal
import sys
from typing import List

from file_system_manager import FileSystemManager
from parser_command import Parser
from error_messages import ErrorMessages

is_running: bool = True
STOP_EXECUTION_SIGNALS: List = [signal.SIGINT, signal.SIGTERM]


def exit_type_signal_handler(signum, frame):
    global is_running
    is_running = False


for sig in STOP_EXECUTION_SIGNALS:
    signal.signal(sig, exit_type_signal_handler)


def main():
    file_system_manager = FileSystemManager()
    parser = Parser()

    while is_running:
        current_dir = file_system_manager.show_current_directory()
        try:
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
            print("Successfully..")
        else:
            print(ErrorMessages.GeneralError.value)
        print(file_system_manager.memory_buffer.tolist()[:50])

    # This block will always execute, ensuring create_backup is called
    while True:
        result = input("Create backup? (y/n) ").strip().lower()
        if result == 'y':
            file_system_manager.create_backup()
            break
        elif result == 'n':
            break


if __name__ == "__main__":
    main()
