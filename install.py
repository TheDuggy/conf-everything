from sshkeyboard import listen_keyboard
from colorama import Cursor, Fore, Style
from colorama import Back
from colorama.initialise import init
from enum import Enum
from types import FunctionType
import os

### Constants ###
INFO = "./info"
DATA = "./data"
GRAY = Style.BRIGHT + Fore.BLACK
""""""
LOGO = GRAY + """                        ___
                  ___  |   |  ___
""" + Fore.YELLOW + """  ,ad0000ba, """ + GRAY + """    |   |_|   |_|   |""" + Fore.YELLOW + """   000b      00  00000000000
 d0"'    `"0b""" + GRAY + """    |_     """ + Fore.YELLOW + "____" + GRAY +"""    _|""" + Fore.YELLOW + """   0000b     00  00\"\"\"\"\"\"\"\"\"  
d0'             """ + GRAY + """___|   """ + Fore.YELLOW +"/    \\" + GRAY + """  |___""" + Fore.YELLOW + """  00 `0b    00  00
00             """ + GRAY + """|      """ + Fore.YELLOW + "|      |" + GRAY +"""     |""" + Fore.YELLOW + """ 00  `0b   00  00aaaaa
00             """ + GRAY + """|___   """ + Fore.YELLOW + "|      |" + GRAY + """  ___|""" + Fore.YELLOW + """ 00   `0b  00  00\"\"\"\"\"
Y0,               """ + GRAY + """_|   """ + Fore.YELLOW + "\____/" + GRAY + """  |_""" + Fore.YELLOW + """    00    `0b 00  00 
 Y0a.    .a0P    """ + GRAY + """|    _     _    |""" + Fore.YELLOW + """   00     `0000  00
  `"Y0000Y"'     """ + GRAY + """|___| |   | |___|""" + Fore.YELLOW + """   00      `000  00
                       """ + GRAY + """|___|        """ + Fore.RESET + Style.RESET_ALL
VERSION = "1.0"


class PlatformSupport(Enum):
    WINDOWS = 1
    LINUX = 2
    BOTH = 3

class Menu():
    def __init__(self, prompt: str, options: dict, hover_format: FunctionType, option_prefix: str = Fore.RESET, prompt_prefix: str = Fore.RESET, selected_prefix: str = Fore.RESET) -> None:
        self.options = list(options.keys())
        self.option_prefix = option_prefix
        self.selected_prefix = selected_prefix
        self.selection = self.options[0]
        self.__cursor_pos = len(self.options) - 1
        self.__first_pressed = False
        self.prompt = prompt
        self.prompt_prefix = prompt_prefix
        self.hover_format = hover_format

        # hide cursor
        print("\033[?25l", end="")

        print(f"{prompt_prefix + prompt}: ", end="\n\n")

        # print available options
        for s in options:
            print(f"    {self.option_prefix + s}")
            self.__cursor_pos -= 1 
        print(Cursor.UP(), end="")
        self.__cursor_pos += 1
        self.options.reverse()
        # start keyboard-listener
        try:
            listen_keyboard(on_press=self.__on_press, until="enter", delay_other_chars=0.01, delay_second_char=0.01) 
        except KeyboardInterrupt:
            self.selection = None

        # remove menu-options
        print(Cursor.DOWN(self.__cursor_pos), end="")
        for i in range(0, len(self.options) - 2):
            print(f"\033[2K\033[G{Cursor.UP()}", end="")
        self.__clear_line()

        # print took option
        print(f"{Cursor.UP(3) + Cursor.FORWARD(len(self.prompt) + 2) + self.selected_prefix + self.selection}")

        # show cursor
        print("\033[?25h", end="")
        print(Fore.RESET + Style.RESET_ALL + Back.RESET, end="")
        options[self.selection]()
        
    def __clear_line(self) -> None:
        print("\033[2K\033[G", end="")

    def __on_press(self, key) -> None:
        if key in ["up", "down", "tab"]:
            self.__hover(key)

    def __hover(self, action: str) -> None:

        move = -1 if action == "down" or action == "tab" else 1

        # check the hover-effect hasn't been applied yet
        if self.__first_pressed:

            # remove hover-effect from previous selection
            self.__clear_line()
            print(Fore.RESET + f"{' ' * 4}{self.option_prefix + self.selection}", end="\r")

            self.selection = self.options[((self.options.index(self.selection) + move) + len(self.options)) % len(self.options)]

            if self.__cursor_pos == len(self.options) - 1 and move > 0: # if you are at the menu-top, go to the bottum when <up> is pressed
                print(Cursor.DOWN(len(self.options) - 2))
                self.__cursor_pos = 0
            elif self.__cursor_pos == 0 and move < 0: # if you are at the menu-bottum, go to the top when <down> is pressed
                print(Cursor.UP(len(self.options)))
                self.__cursor_pos = len(self.options) - 1
            else:
                if move < 0:
                    print(Cursor.DOWN(), end = "") # in case of normal movement, just go up or down
                    self.__cursor_pos -= 1
                else:
                    print(Cursor.UP(), end = "")
                    self.__cursor_pos += 1
            
        else:
            # for the first click we hover over the first item
            print(Cursor.UP(len(self.options) - 1), end="")
            self.__cursor_pos = len(self.options) - 1
            self.__first_pressed = True

        # print the hover-effect
        self.__clear_line()
        print(self.hover_format(self.selection), end="\r")
        

class Configuration():
    def __init__(self, id: str, platform: PlatformSupport, conf_version: int) -> None:
        self.id = id
        self.platform = platform
        self.conf_version = conf_version
        self.__validate_folder_structure()


    def __validate_folder_structure(self) -> None:
        if self.platform == PlatformSupport.WINDOWS or self.platform == PlatformSupport.BOTH:
            if not os.path.exists(INFO + "/" + self.id + "/win.bat"):
                raise Exception("Windos install script missing!")

        if self.platform == PlatformSupport.LINUX or self.platform == PlatformSupport.LINUX:
            if not os.path.exists(INFO + "/" + self.id + "/linux.sh"):
                raise Exception("Linux install script missing!")

        if not os.path.exists(DATA + "/" + self.id):
            raise Exception("Data entry missing!")

def main():
    print(type(main))
    init()

    print(LOGO, end = " ")
    print(GRAY + "everything " + Style.RESET_ALL + Fore.BLACK + Back.YELLOW + "v" + VERSION + Fore.RESET + Back.RESET, end="\n\n")

    menu = Menu(prompt="[?] Take your action", options=
        {
            "List configs": lambda: print("Hello"),
            "Create empty config":  lambda: print("Hello"),
            "Update local configs": lambda: print("Hello")
        }, hover_format=lambda option: Fore.CYAN + f"{' ' * 4}  > {option}" + Fore.RESET, option_prefix=Fore.YELLOW, prompt_prefix=Fore.YELLOW, selected_prefix=Fore.CYAN)
    
    print(menu.selection)

if __name__ == '__main__':
    main()
