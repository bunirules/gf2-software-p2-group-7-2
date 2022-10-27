#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
from pathlib import Path

from numpy import character
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""
    try:
        return open(path, "r")
    except Exception as e:
        print(f"ERROR: Could not open file {path}.")
        sys.exit()


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    return input_file.read(1)


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    character = input_file.read(1)
    while character.isspace():
        character = input_file.read(1)
    return character


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    character = input_file.read(1)
    while not character.isdigit():
        if character == "":
            return [None, ""]
        character = input_file.read(1)
    number = character
    character = input_file.read(1)
    while character.isdigit():
        number += character
        if character == "":
            return [number, ""]
        character = input_file.read(1)
    return [number, character]


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    character = input_file.read(1)
    while not character.isalpha():
        if character == "":
            return [None, ""]
        character = input_file.read(1)
    name = character
    character = input_file.read(1)
    while character.isalnum():
        name += character
        if character == "":
            return [name, ""]
        character = input_file.read(1)
    return [name, character]


def main():
    """Preliminary exercises for Part IIA Project GF2."""
    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("\n\nError! One command line argument is required.\n")
        sys.exit()

    else:

        print("\nNow opening file...\n")
        # Print the path provided and try to open the file for reading
        path = Path.cwd().joinpath(arguments[0])
        print(path)
        file = open_file(path)

        print("\n\nNow reading file...\n")
        # Print out all the characters in the file, until the end of file
        character = file.read(1)
        while character != "":
            print(character, sep='', end='')
            character = get_next_character(file)

        print("\n\nNow skipping spaces...\n")
        # Print out all the characters in the file, without spaces
        file.seek(0, 0)
        character = file.read(1)
        while character != "":
            print(character, sep='', end='')
            character = get_next_non_whitespace_character(file)

        print("\n\nNow reading numbers...\n")
        # Print out all the numbers in the file
        file.seek(0, 0)
        character = ""
        number = ""
        while number is not None:
            print(number, sep='', end='\n')
            number, character = get_next_number(file)

        print("\n\nNow reading names...\n")
        # Print out all the names in the file
        file.seek(0, 0)
        character = ""
        name = ""
        while name is not None:
            print(name, sep='', end='\n')
            name, character = get_next_name(file)

        print("\n\nNow censoring bad names...\n")
        # Print out only the good names in the file
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                        name.lookup("Ghastly"), name.lookup("Awful")]
        file.seek(0, 0)
        character = ""
        word = ""
        while word is not None:
            if name.lookup(word) not in bad_name_ids:
                print(word, sep='', end='\n')
            word, character = get_next_name(file)


if __name__ == "__main__":
    main()
