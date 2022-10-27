"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
import sys
from pathlib import Path

import numpy as np


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.position = None
        self.string = None


class Scanner:
    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol
    skip_spaces(self): Skips whitespace to next character
    advance(self): Advances one more character in the file
    backwards(self): Goes back one character in the file
    get_name(self): Gets full name symbol
    get_number(self): Gets full number symbol
    check_comment(self): Checks to see if a second backslash follows the
                         first to signal the start or end of a comment
    print_error(self, symbol, suggestion): Prints error line with marker
                                           and suggestion of error cause
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        # check circuit definition file exists
        if Path(str(path)).is_file():
            # check file is a text file
            if Path(str(path)).suffix == ".txt":
                self.file = open(Path(str(path)), "r")
                self.line_lengths = [len(line) for line in self.file]
                self.file.seek(0, 0)
                self.file_position = 0
                self.names = names
                self.symbol_type_list = [
                    self.COMMA,
                    self.SEMICOLON,
                    self.EQUALS,
                    self.KEYWORD,
                    self.NUMBER,
                    self.ZERO,
                    self.NAME,
                    self.BRACE_LEFT,
                    self.BRACE_RIGHT,
                    self.PARENTHESIS_LEFT,
                    self.PARENTHESIS_RIGHT,
                    self.ARROW,
                    self.DOT,
                    self.EOF,
                    self.INVALID_CHARACTER,
                ] = range(15)
                self.keywords_list = [
                    "CIRCUIT",
                    "DEVICES",
                    "CONNECT",
                    "MONITOR",
                    "END",
                    "CLOCK",
                    "SWITCH",
                    "AND",
                    "NAND",
                    "OR",
                    "NOR",
                    "XOR",
                    "NOT",
                    "DTYPE",
                ]
                [
                    self.CIRCUIT_ID,
                    self.DEVICES_ID,
                    self.CONNECT_ID,
                    self.MONITOR_ID,
                    self.END_ID,
                    self.CLOCK_ID,
                    self.SWITCH_ID,
                    self.AND_ID,
                    self.NAND_ID,
                    self.OR_ID,
                    self.NOR_ID,
                    self.XOR_ID,
                    self.NOT_ID,
                    self.DTYPE_ID,
                ] = self.names.lookup(self.keywords_list)
                self.current_character = self.file.read(1)
                self.comment = False
                self.max_error_line_length = 79
            else:
                print(
                    "\n\nError: Invalid file type. Please choose a text"
                    " file.\n"
                )
                sys.exit()
        else:
            print(
                "\n\nError: Invalid path to file. Please choose a valid"
                " file (include suffix).\n"
            )
            sys.exit()

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace

        if self.current_character == "\\":
            self.comment = self.check_comment()  # check if start of comment
            # if only one backslash -> invalid character selection
            if not self.comment:
                self.backwards()
            while self.comment:
                # if end of file is found while in comment
                if self.current_character == "":
                    break
                # check if comment is finished
                elif self.current_character == "\\":
                    self.comment = self.check_comment()
                self.advance()
            else:
                self.skip_spaces()  # skip whitespace after comment

        symbol.position = self.file_position

        if self.current_character.isalpha():  # letter
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])
            symbol.string = name_string

        elif self.current_character.isdigit():  # number
            if int(self.current_character) == 0:
                symbol.id = 0
                symbol.type = self.ZERO
                self.advance()
            else:
                symbol.id = self.get_number()
                symbol.type = self.NUMBER
            symbol.string = str(symbol.id)

        elif self.current_character == ",":
            symbol.type = self.COMMA
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == "=":
            symbol.type = self.EQUALS
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == "{":
            symbol.type = self.BRACE_LEFT
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == "}":
            symbol.type = self.BRACE_RIGHT
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == "(":
            symbol.type = self.PARENTHESIS_LEFT
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == ")":
            symbol.type = self.PARENTHESIS_RIGHT
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == ">":
            symbol.type = self.ARROW
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == ".":
            symbol.type = self.DOT
            symbol.string = self.current_character
            self.advance()

        elif self.current_character == "":  # end of file
            symbol.type = self.EOF
            symbol.string = self.current_character
            self.advance()

        else:  # not a valid character
            symbol.type = self.INVALID_CHARACTER
            symbol.string = self.current_character
            self.advance()

        # if file ends with open comment
        if symbol.type == self.EOF and self.comment:
            self.print_error(
                symbol, "File ended with open comment. Expected '\\\\'"
            )

        return symbol

    def skip_spaces(self):
        """Skip whitespace to next character."""
        while self.current_character.isspace():
            self.advance()

    def advance(self):
        """Advance one more character."""
        self.current_character = self.file.read(1)
        self.file_position += 1

    def backwards(self):
        """Go back one character."""
        if self.current_character == "":
            self.file.seek(self.file.tell() - 1, 0)
            self.file_position -= 1
        else:
            self.file.seek(self.file.tell() - 2, 0)
            self.file_position -= 2
        self.advance()

    def get_name(self):
        """Get full name symbol."""
        name = self.current_character
        self.advance()
        # get all following alphanumeric characters and add to name
        while self.current_character.isalnum():
            name += self.current_character
            self.advance()

        return name

    def get_number(self):
        """Get full number symbol."""
        number = int(self.current_character)
        self.advance()
        # get all following digits and add to number
        while self.current_character.isdigit():
            number = number * 10 + int(self.current_character)
            self.advance()

        return number

    def check_comment(self):
        """Check to see if this is start or end of a comment."""
        self.advance()
        if self.current_character == "\\":  # if second backslash follows first
            return not self.comment
        return self.comment

    def print_error(self, symbol, suggestion=""):
        """Print error line with marker.

        Arguments:
            symbol -- Symbol that caused the error
            suggestion -- String that suggests correct character
        """
        current_position = self.file.tell()

        # find start of line positions by summing line lengths
        sol_pos = np.array(
            [sum(self.line_lengths[:i]) for i in range(len(self.line_lengths))]
        )
        # positions of first character of lines relative to marker
        sol_pos_rel_marker = sol_pos - symbol.position
        if len(sol_pos_rel_marker) == 0:
            line_text = ""
            position = 0
            line = 1
        else:
            # position on line (starts at 0)
            position = -max([i for i in sol_pos_rel_marker if i <= 0])
            # line of file (starts at 1)
            line = np.where(sol_pos_rel_marker == -position)[0][0] + 1

            # set current position to start of file
            self.file.seek(0, 0)

            # split file by line breaks to get error line text
            line_text = self.file.read().split("\n")[line - 1]

        # shorten output if line is very long
        if len(line_text) > self.max_error_line_length:
            # shorten before marker
            if position > (self.max_error_line_length + 1) // 2 - 5:
                line_text = (
                    "[...]"
                    + line_text[
                        (
                            position
                            - (self.max_error_line_length + 1) // 2
                            + 6
                        ) :
                    ]
                )
                position = (self.max_error_line_length - 1) // 2
            # shorten after marker
            if (
                len(line_text) - position
                > (self.max_error_line_length + 1) // 2
            ):
                line_text = (
                    line_text[
                        : position + (self.max_error_line_length) // 2 - 4
                    ]
                    + "[...]"
                )

        output = (
            f"Error on line {line}:\n\n"
            + line_text
            + "\n"
            + " " * position
            + "^\n\n"
            + suggestion
        )
        print("\n\n" + output)

        self.file.seek(current_position, 0)

        return output
