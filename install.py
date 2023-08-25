from colorama import Fore
from colorama import Back
from colorama.initialise import init
from enum import Enum

class PlatformSupport(Enum):
    WINDOWS = 1
    LINUX = 2
    BOTH = 3

class Configuration():
    def __init__(self, id: str, platform: PlatformSupport) -> None:
        self.id = id
        self.platform = platform

def main():
    init()

    print(Fore.GREEN + 'Hello!')

if __name__ == '__main__':
    main()
