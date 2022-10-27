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


def test_parser_returns_true():
    parser = new_parser(str(Path("test_files/test_parser1.1.txt")))
    assert parser.parse_network() == True


@pytest.mark.parametrize(
    "path", ["test_files/test_parser1.2.txt", 
            "test_files/test_parser1.3.txt",
            "test_files/test_parser1.4.txt",
            "test_files/test_parser1.5.txt",
            "test_files/test_parser1.6.txt",
            "test_files/test_parser1.7.txt",
            "test_files/test_parser1.8.txt",
            "test_files/test_parser1.9.txt",
            "test_files/test_parser1.10.txt",
            "test_files/test_parser1.11.txt",
            "test_files/test_parser1.12.txt",
            "test_files/test_parser1.13.txt",
            "test_files/test_parser1.14.txt",
            "test_files/test_parser1.15.txt",
            "test_files/test_parser1.16.txt",
            "test_files/test_parser1.17.txt",
            "test_files/test_parser1.18.txt",
            "test_files/test_parser1.19.txt",
            "test_files/test_parser1.20.txt",
            "test_files/test_parser1.21.txt",
            "test_files/test_parser1.22.txt",
            "test_files/test_parser1.23.txt",
            "test_files/test_parser1.24.txt",
            "test_files/test_parser1.25.txt",
            "test_files/test_parser1.26.txt",
            "test_files/test_parser1.27.txt",]
)

def test_parser_returns_false(path):
    parser = new_parser(str(Path(path)))
    assert parser.parse_network() == False


def test_parser_missing_equals():       # - instead of = in DEVICES
    parser = new_parser(str(Path("test_files/test_parser1.2.txt")))
    assert parser.parse_network() == ""


def test_parser_missing_dot():     # : instead of . in CONNECT
    parser = new_parser(str(Path("test_files/test_parser1.3.txt")))
    assert parser.parse_network() == ""


def test_parser_missing_arrow():        # = instead of > in CONNECT
    parser = new_parser(str(Path("test_files/test_parser1.4.txt")))
    assert parser.parse_network() == ""


def test_parser_missing_MONITOR():      # MONITOR misspelled
    parser = new_parser(str(Path("test_files/test_parser1.5.txt")))
    assert parser.parse_network() == ""


def test_parser_missing_close_brace():      # missing brace end of CONNECT
    parser = new_parser(str(Path("test_files/test_parser1.6.txt")))
    assert parser.parse_network() == ""


def test_parser_missing_open_brace():       # missing brace after CIRCUIT
    parser = new_parser(str(Path("test_files/test_parser1.7.txt")))
    assert parser.parse_network() == ""


def test_parser_missing_END():      # END misspelled
    parser = new_parser(str(Path("test_files/test_parser1.8.txt")))
    assert parser.parse_network() == ""


def test_parser_bad_name():     # 4SW4 as a name definition
    parser = new_parser(str(Path("test_files/test_parser1.9.txt")))
    assert parser.parse_network() == ""


def test_parser_missing_semicolon():    # missing semicolon in MONITOR
    parser = new_parser(str(Path("test_files/test_parser1.10.txt")))
    assert parser.parse_network() == ""


def test_parser_bad_clock_param():      # clock parameter is zero
    parser = new_parser(str(Path("test_files/test_parser1.11.txt")))
    assert parser.parse_network() == ""


def test_parser_bad_switch_param():     # switch parameter is two
    parser = new_parser(str(Path("test_files/test_parser1.12.txt")))
    assert parser.parse_network() == ""


def test_parser_bad_gate_param_0():       # and gate parameter is 0
    parser = new_parser(str(Path("test_files/test_parser1.13.txt")))
    assert parser.parse_network() == ""


def test_parser_bad_device_definition():      # errors in switch definition
    parser = new_parser(str(Path("test_files/test_parser1.14.txt")))
    assert parser.parse_network() == ""


def test_parser_xor_param():        # xor gate has a parameter
    parser = new_parser(str(Path("test_files/test_parser1.15.txt")))    
    assert parser.parse_network() == ""


def test_parser_unsupported_device():   # declare unsupported device type
    parser = new_parser(str(Path("test_files/test_parser1.16.txt")))
    assert parser.parse_network() == ""


def test_parser_no_gate_param1():    # forgot to initialise a gate parameter
    parser = new_parser(str(Path("test_files/test_parser1.17.txt")))
    assert parser.parse_network() == ""


def test_parser_no_gate_param2():   # forgot to initialise a gate parameter
    parser = new_parser(str(Path("test_files/test_parser1.18.txt")))
    assert parser.parse_network() == ""


def test_parser_switch_param_is_01():   # switch parameter is 01
    parser = new_parser(str(Path("test_files/test_parser1.19.txt")))
    assert parser.parse_network() == ""


def test_parser_bad_pinname():   # and1 pinname is 1 instead of I1
    parser = new_parser(str(Path("test_files/test_parser1.20.txt")))
    assert parser.parse_network() == ""


def test_parser_multiple_errors():   # multiple minor syntax errors
    parser = new_parser(str(Path("test_files/test_parser1.21.txt")))
    assert parser.parse_network() == ""
    assert parser.num_errors == 18


def test_parser_no_braces():   # missing all braces
    parser = new_parser(str(Path("test_files/test_parser1.22.txt")))
    assert parser.parse_network() == ""
    assert parser.num_errors == -1


def test_parser_no_semicolons():   # missing all semicolons
    parser = new_parser(str(Path("test_files/test_parser1.23.txt")))
    assert parser.parse_network() == ""
    assert parser.num_errors == -1


def test_parser_no_commas():   # missing all commas
    parser = new_parser(str(Path("test_files/test_parser1.24.txt")))
    assert parser.parse_network() == ""
    assert parser.num_errors == -1


def test_parser_no_stopping_symbols():   # missing all stopping symbols
    parser = new_parser(str(Path("test_files/test_parser1.25.txt")))
    assert parser.parse_network() == ""
    assert parser.num_errors == -1


def test_parser_no_keywords():   # missing CIRCUIT, DEVICES etc
    parser = new_parser(str(Path("test_files/test_parser1.26.txt")))
    assert parser.parse_network() == ""
    assert parser.num_errors == -1


def test_parser_no_right_brace():   # missing all right braces
    parser = new_parser(str(Path("test_files/test_parser1.27.txt")))
    assert parser.parse_network() == ""
    assert parser.num_errors == -1