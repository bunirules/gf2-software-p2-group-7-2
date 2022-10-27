import pytest
from pathlib import Path
from scanner import *
from names import Names


def test_symbol():
    names = Names()
    scanner = Scanner(str(Path("test_files/test0.txt")), names)
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
        "G1",
        ".",
        "I1",
        ";",
        "SW2",
        ">",
        "G2",
        ".",
        "I2",
        ";",
        "G2",
        ">",
        "G1",
        ".",
        "I2",
        ";",
        "G1",
        ">",
        "G2",
        ".",
        "I1",
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


def test_scanner_spaces():
    names1 = Names()
    names2 = Names()
    names3 = Names()
    scanner1 = Scanner(str(Path("test_files/test_scanner1a.txt")), names1)
    scanner2 = Scanner(str(Path("test_files/test_scanner1b.txt")), names2)
    scanner3 = Scanner(str(Path("test_files/test_scanner1c.txt")), names3)
    for i in range(15):
        symbol1 = scanner1.get_symbol()
        symbol2 = scanner2.get_symbol()
        symbol3 = scanner3.get_symbol()
        assert symbol1.type == symbol2.type == symbol3.type
        assert symbol1 is not None


def test_line_break():
    names1 = Names()
    scanner1 = Scanner(str(Path("test_files/test2a.txt")), names1)
    names2 = Names()
    scanner2 = Scanner(str(Path("test_files/test2b.txt")), names2)
    while True:
        symbol1 = scanner1.get_symbol()
        symbol2 = scanner2.get_symbol()
        assert symbol1.string == symbol2.string
        if symbol1.string == "":
            break


def test_scanner_comments():
    names1 = Names()
    names2 = Names()
    scanner1 = Scanner(str(Path("test_files/test_scanner3a.txt")), names1)
    scanner2 = Scanner(str(Path("test_files/test_scanner3b.txt")), names2)
    for i in range(215):
        symbol1 = scanner1.get_symbol()
        symbol2 = scanner2.get_symbol()
        assert symbol1.type == symbol2.type
        assert symbol1 is not None


def test_complex_comments():
    names1 = Names()
    scanner1 = Scanner(str(Path("test_files/test4a.txt")), names1)
    names2 = Names()
    scanner2 = Scanner(str(Path("test_files/test4b.txt")), names2)
    while True:
        symbol1 = scanner1.get_symbol()
        symbol2 = scanner2.get_symbol()
        assert symbol1.string == symbol2.string
        if symbol1.string == "":
            break


def test_scanner_error_message():
    names1 = Names()
    scanner1 = Scanner(str(Path("test_files/test_scanner5a.txt")), names1)
    for i in range(13):
        scanner1.get_symbol()
    test_symbol = scanner1.get_symbol()
    assert (
        scanner1.print_error(test_symbol)
        == "Error on line 6:\n\n    SW1, SW2, SW3, SW4, SW5 - SWITCH(0);\n"
        + "                            ^\n\n"
    )

    names2 = Names()
    scanner2 = Scanner(str(Path("test_files/test_scanner5b.txt")), names2)
    for i in range(21):
        scanner2.get_symbol()
    test_symbol = scanner2.get_symbol()
    assert (
        scanner2.print_error(test_symbol) ==
        "Error on line 7:\n\n    nand1, 22, nand3, nand4 = NAND(2);\n"
        + "           ^\n\n"
    )

    names3 = Names()
    scanner3 = Scanner(str(Path("test_files/test_scanner5c.txt")), names3)
    for i in range(88):
        scanner3.get_symbol()
    test_symbol = scanner3.get_symbol()
    assert (
        scanner3.print_error(test_symbol)
        == "Error on line 19:\n\n    SW2 > xor1:I2, nor1.I1;\n"
        + "              ^\n\n"
    )

    names4 = Names()
    scanner4 = Scanner(str(Path("test_files/test_scanner5d.txt")), names4)
    for i in range(30):
        scanner4.get_symbol()
    test_symbol = scanner4.get_symbol()
    assert (
        scanner4.print_error(test_symbol)
        == "Error on line 7:\n\n    nand1, nand2, nand3, nand4 = NAND(2];\n"
        + "                                       ^\n\n"
    )

    names5 = Names()
    scanner5 = Scanner(str(Path("test_files/test_scanner5e.txt")), names5)
    test_symbol = scanner5.get_symbol()
    assert (
        scanner5.print_error(test_symbol)
        == "Error on line 1:\n\nCIRCUITO{}\n^\n\n"
    )


def test_error_message_2():
    names = Names()
    scanner = Scanner(str(Path("test_files/test6.txt")), names)
    for i in range(35):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()

    assert (
        scanner.print_error(test_symbol)
        == "Error on line 8:\n\n    nor1, nor2: NOR(2);\n              ^\n\n"
    )


def test_error_message_multiple_errors():
    names = Names()
    scanner = Scanner(str(Path("test_files/test_scanner7.txt")), names)
    for i in range(7):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 6:\n\n    SW1, SW2/ SW3, SW4, SW5 = SWITCH(0);\n"
        + "            ^\n\n"
    )
    for i in range(22):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 7:\n\n    nand1, nand2, nand3, nand4 = NAND(2};\n"
        + "                                       ^\n\n"
    )
    for i in range(13):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 9:\n\n    xor1, xor2 + XOR;\n               ^\n\n"
    )
    for i in range(11):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 11:\n\n    and1 = SAND(2);\n           ^\n\n"
    )
    for i in range(17):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 14:\n\n    inv1 = NOT(1);\n           ^\n\n"
    )
    for i in range(48):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 23:\n\n    or1 } nand1.I2;\n        ^\n\n"
    )
    for i in range(25):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 26:\n\n    nand2 > nor2.I2} nand3.I1;\n"
        + "                   ^\n\n"
    )
    for i in range(64):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 34:\n\n    dt1.QBAR > nand4.I1;;\n"
        + "                        ^\n\n"
    )
    for i in range(6):
        scanner.get_symbol()
    test_symbol = scanner.get_symbol()
    assert (
        scanner.print_error(test_symbol)
        == "Error on line 40:\n\n}\n^\n\n"
    )
