#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""
    fo = open(path,'r')
    return fo


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    next_character = input_file.read(1)
    return next_character


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    next_character = input_file.read(1)
    if next_character.isspace():
        next_character = get_next_non_whitespace_character(input_file)
    return next_character

def get_file_length(input_file):
    pos = input_file.tell()
    input_file.read()
    length = input_file.tell()
    input_file.seek(pos,0)
    return length

def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    length = get_file_length(input_file)
    next_number = ''
    next_digit = input_file.read(1)
    for i in range(length):
        if not next_digit.isdigit():
            next_digit = input_file.read(1)
        elif next_digit.isdigit():
            break
    for i in range(length):
        next_number += next_digit
        next_digit = input_file.read(1)
        if not next_digit.isdigit():
            break
    if next_number == '':
        return [None, '']
    else:
        return [int(next_number), next_digit]

def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    length = get_file_length(input_file)
    next_name = ''
    next_char = input_file.read(1)
    for i in range(length):
        if not next_char.isalpha():
            next_char = input_file.read(1)
        elif next_char.isalpha():
            break
    for i in range(length):
        next_name += next_char
        next_char = input_file.read(1)
        if not next_char.isalnum():
            break
    if next_name == '':
        return [None, '']
    else:
        return [next_name, next_char]

def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:

        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading

        path = arguments[0]
        
        fo = open_file(path)

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file

        char = ' '
        while char!='':
            char = get_next_character(fo)
            print(char, sep = '', end = '')
        
        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces

        fo.seek(0,0)
        char = ' '
        while char!='':
            char = get_next_non_whitespace_character(fo)
            print(char, sep = '', end = '')

        print("\nNow reading numbers...")
        # Print out all the numbers in the file

        fo.seek(0,0)
        num = [None, ' ']
        while num[1] != '':
            num = get_next_number(fo)
            if num[0] is not None:
                print(num[0])

        print("\nNow reading names...")
        # Print out all the names in the file

        fo.seek(0,0)
        new_name = [None, ' ']
        while new_name[1] != '':
            new_name = get_next_name(fo)
            if new_name[0] is not None:
                print(new_name[0])

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                         name.lookup("Ghastly"), name.lookup("Awful")]
        fo.seek(0,0)
        new_name = [None, ' ']
        while new_name[1] != '':
            new_name = get_next_name(fo)
            new_name_id = name.lookup(new_name[0])
            if new_name_id not in bad_name_ids:
                if name.get_string(new_name_id) is not None:
                    print(name.get_string(new_name_id))

if __name__ == "__main__":
    main()
