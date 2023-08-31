from FileSystemManager import FileSystemManager
from Parser import Parser


def main():
    file_system_manager = FileSystemManager()
    parser = Parser(file_system_manager)
    parser.main_loop()


if __name__ == "__main__":
    main()
