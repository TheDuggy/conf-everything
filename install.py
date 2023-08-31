from sshkeyboard import listen_keyboard
from time import sleep
from math import floor, ceil
from re import search, match
from json import dump, load
from colorama import Cursor, Fore, Style, Back
from colorama.initialise import init
from enum import Enum
from types import FunctionType
import os

### Constants ###
INFO = "./info"
DATA = "./data"
GRAY = Style.BRIGHT + Fore.BLACK
""""""
LOGO = GRAY + Style.RESET_ALL + """                        ___
                  ___  |   |  ___
""" + Fore.YELLOW + """  ,ad0000ba, """ + GRAY + Style.RESET_ALL + Style.RESET_ALL + """    |   |_|   |_|   |""" + Fore.YELLOW + """   000b      00  00000000000
 d0"'    `"0b""" + GRAY + Style.RESET_ALL + """    |_     """ + Fore.YELLOW + "____" + GRAY + Style.RESET_ALL +"""    _|""" + Fore.YELLOW + """   0000b     00  00\"\"\"\"\"\"\"\"\"  
d0'             """ + GRAY + Style.RESET_ALL + """___|   """ + Fore.YELLOW +"/    \\" + GRAY + Style.RESET_ALL + """  |___""" + Fore.YELLOW + """  00 `0b    00  00
00             """ + GRAY + Style.RESET_ALL + """|      """ + Fore.YELLOW + "|      |" + GRAY + Style.RESET_ALL +"""     |""" + Fore.YELLOW + """ 00  `0b   00  00aaaaa
00             """ + GRAY + Style.RESET_ALL + """|___   """ + Fore.YELLOW + "|      |" + GRAY + Style.RESET_ALL + """  ___|""" + Fore.YELLOW + """ 00   `0b  00  00\"\"\"\"\"
Y0,               """ + GRAY + Style.RESET_ALL + """_|   """ + Fore.YELLOW + "\____/" + GRAY + Style.RESET_ALL + """  |_""" + Fore.YELLOW + """    00    `0b 00  00 
 Y0a.    .a0P    """ + GRAY + Style.RESET_ALL + """|    _     _    |""" + Fore.YELLOW + """   00     `0000  00
  `"Y0000Y"'     """ + GRAY + Style.RESET_ALL + """|___| |   | |___|""" + Fore.YELLOW + """   00      `000  00
                       """ + GRAY + Style.RESET_ALL + """|___|        """ + Fore.RESET + Style.RESET_ALL
VERSION = "1.0"
chached_configs = []

class Logging():
    def fatal(self, msg: str) -> None:
        print(f"{Back.RESET + Style.RESET_ALL + Fore.RED}[-] {msg + Fore.RESET}")

    def info(self, msg: str) -> None:
        print(f"{Back.RESET + Style.RESET_ALL + Fore.CYAN}[~]{msg + Fore.RESET}")
    
    def warning(self, msg: str) -> None:
        print(f"\033[1m{Back.RESET + Style.RESET_ALL + Fore.YELLOW}[!] {msg + Fore.RESET}")
LOGGER = Logging()

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
        if self.__cursor_pos > 0:
            print(Cursor.DOWN(self.__cursor_pos), end="")
        print(self.__cursor_pos, "")
        for i in range(0, len(self.options) + 1):
           print(f"\033[2K\033[G{Cursor.UP()}", end="")

        # print took option
        print(f"{Cursor.UP() + Cursor.FORWARD(len(self.prompt) + 2) + self.selected_prefix + (self.selection if self.selection != None else 'None')}")

        # show cursor and reset colors
        print("\033[?25h", end="")
        print(Fore.RESET + Style.RESET_ALL + Back.RESET, end="")

        # if selected run selected function
        if self.selection != None:
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

class Scrollable():
    def __init__(self, w_h: tuple, entries: list) -> None:
        self.w = w_h[0]
        self.h = w_h[1]
        self.entries = entries
        if not self.h >= 3:
            raise ValueError("<h> must be at least 3 for scroll-bar!")
        self.__last_shown = self.h - 1
        self.__first_shown = 0
        self.__hover_pos = None
        self.__term_size_h = os.get_terminal_size()[1]
        print("\033[?25l", end="")

        print(f"{'-' * floor((self.w + 3) / 2)}ƒ{'-' * floor((self.w + 3) / 2)}")
        for i in range(0, self.h if self.h <= len(self.entries) else len(self.entries)):
            print(self.__validate_entryname(self.entries[i]))
        print('-' * (self.w + 3))
        print(Cursor.UP(self.h + 1), end="")
        try:
            listen_keyboard(on_press=self.__on_press, until="enter", delay_other_chars=0.01, delay_second_char=0.01) 
        except KeyboardInterrupt:
            pass
        
        print(f"{Cursor.UP()}\033[2K\033[G{Cursor.UP()}")
        print("\033[?25h", end="")
        sleep(10)

            
    def __validate_entryname(self, entryname: str) -> str:
        if len(entryname) > self.w:
            return entryname[:(self.w - 3)] + "..."
        return entryname
    
    def __on_press(self, key):
        if key in ["down", "tab"]:
            self.__select(1)
        elif key == "up":
            self.__select(-1)

    def __select(self, move: int):

        if self.__term_size_h != os.get_terminal_size()[1]:
            dif = os.get_terminal_size()[1] - self.__term_size_h
            if dif < 0:
                print(Cursor.UP(), end="")
            self.__term_size_h = os.get_terminal_size()[1]
            

        if self.__hover_pos == None:
            self.__hover_pos = 0
        else:
            if self.__hover_pos == self.__last_shown and move == 1:
                if self.__hover_pos < len(self.entries) - 1:
                    self.__last_shown += 1
                    self.__first_shown += 1
                else:
                    self.__last_shown = self.h - 1
                    self.__first_shown = 0
            elif self.__hover_pos == self.__first_shown and move == -1:
                if self.__hover_pos > 0:
                    self.__last_shown -= 1
                    self.__first_shown -= 1
                else:
                    self.__last_shown = len(self.entries) - 1
                    self.__first_shown = len(self.entries) - self.h
            self.__hover_pos = (self.__hover_pos + move) % len(self.entries)
        
        
    

        for i in range(self.__first_shown, self.__last_shown + 1):
            print("\033[2K\033[G", end="")
            if self.__hover_pos == i:
                print(Back.YELLOW + Fore.BLACK, end="")
            else:
                print(Fore.YELLOW, end="")
            print(f"{self.__validate_entryname(self.entries[i]) if i < len(self.entries) else ''}", end="")

            draw_bar = floor(self.h * (self.__hover_pos / len(self.entries))) == i - self.__first_shown

            if draw_bar:
                print(f"{Back.RESET + Fore.RESET + ' ' * ((self.w + 3) - len(self.__validate_entryname(self.entries[i]))) + Back.YELLOW + Fore.BLACK}||{Back.RESET + Fore.YELLOW} {self.__hover_pos + 1}/{len(self.entries)}", end="")

            if len(self.entries[i]) > self.w and self.__hover_pos == i:
                print("\x1b[3m" + Back.RESET + GRAY + f"  ({self.entries[i]})" + Fore.RESET + "\x1b[0m")
            else:
                print() 
            print(Back.RESET + Fore.RESET, end="")
        print(Cursor.UP(self.h), end="")

    
        
        
        
        
        

class Configuration():
    def __init__(self, json_str: str) -> None:
        json_data = load(json_str)
        self.id = str(json_data["id"])
        self.platform = str(json_data["platform"])
        self.conf_version = str(json_data["conf_version"])
        self.display_name = str(json_data["display_name"])
        self.__validate_folder_structure()


    def __validate_folder_structure(self) -> None:
        if self.platform == PlatformSupport.WINDOWS or self.platform == PlatformSupport.BOTH:
            if not os.path.exists(INFO + "/" + self.id + "/win.bat"):
                raise FileNotFoundError("Windows install script missing!")

        if self.platform == PlatformSupport.LINUX or self.platform == PlatformSupport.LINUX:
            if not os.path.exists(INFO + "/" + self.id + "/linux.sh"):
                raise FileNotFoundError("Linux install script missing!")

        if not os.path.exists(DATA + "/" + self.id):
            raise FileNotFoundError("Config-data missing!")

def cache_configs() -> None:
    for f in os.listdir(INFO):
        try:
            conf_id = f
            match = search(r"(.+)\.(.+)$", f)
            if match:
                conf_id = match.group()
            
            with open(f, "r") as json_file:
                list.append(cache_configs, Configuration(json_file.read().splitlines()))
        except Exception as e:
            LOGGER.warning(f"Failed to cache config {f}: ({e.__class__.__name__}) {str(e)}")

def list_configs() -> None:
    pass

def main():
    LOGGER.warning("Hello")
    init()

    print(LOGO, end = " ")
    print(GRAY + Style.RESET_ALL + "everything " + Style.RESET_ALL + Fore.BLACK + Back.YELLOW + "v" + VERSION + Fore.RESET + Back.RESET, end="\n\n")

    menu = Menu(prompt="[?] Take your action", options=
        {
            "List configs": list_configs,
            "Create empty config":  lambda: print("Hello"),
            "Update local configs": lambda: print("Hello")
        }, hover_format=lambda option: Fore.CYAN + f"{' ' * 4}  > {option}" + Fore.RESET, option_prefix=Fore.YELLOW, prompt_prefix=Fore.YELLOW, selected_prefix=Fore.CYAN)
    
    #print(menu.selection)

if __name__ == '__main__':
    main()
