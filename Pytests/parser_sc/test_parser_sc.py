"""Test the parser module."""
import pytest
from pathlib import Path

from names import Names
from scanner import Scanner
from parse import Parser
from network import Network
from devices import Devices
from monitors import Monitors


def new_parser(path):
    """Return a new parser instance"""
    names = Names()
    devices = Devices(names)
    scanner = Scanner(path, names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner)
    return parser


def test_parser_input_to_input(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.1.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 22:\n\n    or1.I1 > nand1.I2;\n                 "
        "  ^\n\nInput already connected\nError Count: 1\n"
    )


def test_parser_output_to_output(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.2.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 21:\n\n    xor1 > nand1.I1, nor1;\n        "
        " ^\n\nOutput connected to output\nError Count: 1\n"
    )


def test_parser_input_not_connected(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.3.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 16:\n\nCONNECT\n^\n\nunconnected inputs:"
        " nand3.I1 xor2.I1 \nError Count: 1\n"
    )


def test_parser_multiple_connections_to_input(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.4.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 28:\n\n    and1 > dt1.DATA, nand2.I1;\n         "
        "                  ^\n\nInput already connected\nError Count: 1\n"
    )


def test_parser_devicename_not_found(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.5.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 18:\n\n    SW1 > xor1.I1, or1.I1;\n         "
        " ^\n\nSpecified device does not exist\nError Count: 1\n"
    )


def test_parser_pinname_not_found(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.6.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 27:\n\n    nand3 > and1.I3, nand4.I2;\n         "
        "        ^\n\nSpecified port does not exist\nError Count: 1\n"
    )


def test_parser_too_many_inputs(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.7.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 11:\n\n    and1 = AND(17);\n              "
        " ^\n\nNumber of inputs must be between 1-16\nError Count: 1\n"
    )


def test_parser_devicename_keyword(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.8.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 13:\n\n    DEVICES = DTYPE;\n    ^\n\nNames"
        " cannot"
        " be Keywords: 'CIRCUIT', 'DEVICES', 'CONNECT', 'MONITOR',"
        " 'END','CLOCK', 'SWITCH', 'AND', 'NAND', 'OR', 'NOR', 'XOR',"
        " 'DTYPE'\nError Count: 1\n"
    )


def test_parser_pinname_keyword(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.9.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 31:\n\n    SW5 > dt1.CONNECT;\n             "
        " ^\n\nNames cannot be Keywords: 'CIRCUIT', 'DEVICES', 'CONNECT',"
        " 'MONITOR', 'END','CLOCK', 'SWITCH', 'AND', 'NAND', 'OR', 'NOR',"
        " 'XOR', 'DTYPE'\nError Count: 1\n"
    )


def test_parser_semantic_semantic(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.10a.txt")))
    assert not parser.parse_network()
    assert parser.error_count == 2
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 11:\n\n    and1 = AND(17);\n              "
        " ^\n\nNumber of inputs must be between 1-16\n\n\nError on line"
        " 13:\n\n    DEVICES = DTYPE;\n    ^\n\nNames cannot be Keywords:"
        " 'CIRCUIT', 'DEVICES', 'CONNECT', 'MONITOR', 'END','CLOCK',"
        " 'SWITCH', 'AND', 'NAND', 'OR', 'NOR', 'XOR', 'DTYPE'\nError"
        " Count: 2\n"
    )


def test_parser_semantic_semantic2(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.10b.txt")))
    assert not parser.parse_network()
    assert parser.error_count == 1
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 18:\n\n    SW11 > xor1.I1, or1.I1;\n   "
        " ^\n\nSpecified device does not exist\nError Count: 1\n"
    )


def test_parser_semantic_syntax(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.11.txt")))
    assert not parser.parse_network()
    assert parser.error_count == 2
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 18:\n\n    SW11 > xor1.I1, or1.I1;\n   "
        " ^\n\nSpecified device does not exist\n\n\nError on line 24:\n\n  "
        "  nand1 < nand2.I1;\n          ^\n\nExpected '>'\nError Count: 2\n"
    )


def test_parser_syntax_semantic(capfd):
    parser = new_parser(str(Path("test_files/test_parser2.12.txt")))
    assert not parser.parse_network()
    assert parser.error_count == 1
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 6:\n\n    SW1, SW2, SW3, SW4, SW5 - SWITCH(0);\n"
        "                            ^\n\nExpected '=' or ','\nError"
        " Count: 1\n"
    )
