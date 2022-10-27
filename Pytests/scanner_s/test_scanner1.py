import pytest
from pathlib import Path

from scanner import *
from names import Names


def test_symbol():
    names = Names()
    scanner = Scanner(str(Path("test_files/test1.txt")), names)
    test_string = [
        "CIRCUIT",
        "{",
        "DEVICES",
        "{",
        "SW1",
        ",",
        "SW2",
        "=",
        "SWITCH",
        "(",
        "OFF",
        ")",
        ";",
        "G1",
        ",",
        "G2",
        "=",
        "NAND",
        "(",
        "2",
        ")",
        ";",
        "}",
        "CONNECT",
        "{",
        "SW1",
        ">",
        "G1.I1",
        ";",
        "SW2",
        ">",
        "G2.I2",
        ";",
        "G2",
        ">",
        "G1.I2",
        ";",
        "G1",
        ">",
        "G2.I1",
        ";",
        "}",
        "MONITORS",
        "{",
        "G1",
        ";",
        "G2",
        ";",
        "}",
        "}",
    ]

    for symbol in test_string:
        assert symbol == scanner.get_symbol().string


def test_line_break():
    names1 = Names()
    scanner1 = Scanner(str(Path("test_files/test2a.txt")), names1)
    names2 = Names()
    scanner2 = Scanner(str(Path("test_files/test2b.txt")), names2)
    while True:
        assert scanner1.get_symbol().string == scanner2.get_symbol.string()
        if scanner1.get_symbol().string == "":
            break


def test_complex_comments():
    names1 = Names()
    scanner1 = Scanner(str(Path("test_files/test4a.txt")), names1)
    names2 = Names()
    scanner2 = Scanner(str(Path("test_files/test4b.txt")), names2)
    while True:
        assert scanner1.get_symbol().string == scanner2.get_symbol.string()
        if scanner1.get_symbol().string == "":
            break

# def test_error_message():
#     names = Names()
#     scanner = Scanner(str(Path("test_files/test5.txt")), names)
#     for i in range(35):
#         scanner.get_symbol()
#     test_symbol = scanner.get_symbol()

#     assert scanner.print_error(test_symbol) == "Error on line 8:\n 'nor2:\n      ^\n    NOR(2)'"
