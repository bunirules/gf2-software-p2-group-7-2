"""Test the scanner module."""
import pytest
import sys
from pathlib import Path

from scanner import Scanner
from names import Names


def test_scanner_spaces():
    names1 = Names()    
    names2 = Names()
    names3 = Names()    
    scanner1 = Scanner(str(Path("test_files/test_scanner1.1.txt")),names1)
    scanner2 = Scanner(str(Path("test_files/test_scanner1.2.txt")),names2)
    scanner3 = Scanner(str(Path("test_files/test_scanner1.3.txt")),names3)
    for i in range(15):
        symbol1 = scanner1.get_symbol()
        symbol2 = scanner2.get_symbol()
        symbol3 = scanner3.get_symbol()
        assert symbol1.type == symbol2.type == symbol3.type      
        assert symbol1 != None

test_scanner_spaces()

def test_scanner_comments():
    names1 = Names()
    names2 = Names()
    scanner1 = Scanner(str(Path("test_files/test_scanner3.1.txt")),names1)
    scanner2 = Scanner(str(Path("test_files/test_scanner3.2.txt")),names2)
    for i in range(215):
        symbol1 = scanner1.get_symbol()
        symbol2 = scanner2.get_symbol()
        assert symbol1.type == symbol2.type
        assert symbol1 != None

def test_scanner_error_message():
    names1 = Names()
    scanner1 = Scanner(str(Path("test_files/test_scanner5.1.txt")),names1)
    for i in range(13):
        scanner1.get_symbol()
    test_symbol = scanner1.get_symbol()
    assert scanner1.print_error(test_symbol) == "Error on line 6:\n' SW5 - SWITCH(OFF);'\n      ^"  
    names2 = Names()
    scanner2 = Scanner(str(Path("test_files/test_scanner5.2.txt")),names2)
    for i in range(19):
        scanner2.get_symbol()
    test_symbol = scanner2.get_symbol()
    assert scanner2.print_error(test_symbol) == "Error on line 7:\n' 22,'\n  ^"
    names3 = Names()
    scanner3 = Scanner(str(Path("test_files/test_scanner5.3.txt")),names3)
    for i in range(88):
        scanner3.get_symbol()
    test_symbol = scanner3.get_symbol()
    assert scanner3.print_error(test_symbol) == "Error on line 19:\n'SW2 > xor1:I2,,\n           ^"

    names4 = Names()    
    scanner4 = Scanner(str(Path("test_files/test_scanner5.4.txt")),names4)
    for i in range(30):
        scanner4.get_symbol()
    test_symbol = scanner4.get_symbol()
    assert scanner4.print_error(test_symbol) == "Error on line 7:\n' nand4 = NAND(2];,\n                 ^"

    names5 = Names()
    scanner5 = Scanner(str(Path("test_files/test_scanner5.5.txt")),names5)
    test_symbol = scanner5.get_symbol()
    assert scanner5.print_error(test_symbol) == "Error on line 1:\n'CIRCUITO{'\n ^"