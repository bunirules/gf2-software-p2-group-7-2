"""Test the parser module."""
import pytest
from pathlib import Path

from names import Names
from scanner import Scanner
from parse import Parser
from network import Network
from devices import Devices
from monitors import Monitors
from translate import Translator
import builtins
import wx 

builtins._ = wx.GetTranslation

def new_parser(path):
    """Return a new parser instance"""
    names = Names()
    devices = Devices(names)
    scanner = Scanner(path, names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    translator = Translator()
    parser = Parser(names, devices, network, monitors, scanner)
    return parser


def test_parser_returns_true():
    """Test parser returns true for valid circuit definition file"""
    parser = new_parser(str(Path("test_files/test_parser1.1.txt")))
    assert parser.parse_network() == True


@pytest.mark.parametrize(
    "path",
    [
        "test_files/test_parser1.2.txt",
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
        "test_files/test_parser1.27.txt",
    ],
)
def test_parser_returns_false(path):
    """Test parser returns false for incorrect circuit definition files"""
    parser = new_parser(str(Path(path)))
    assert parser.parse_network() == False


def test_parser_missing_equals(capfd):  # - instead of = in DEVICES
    """Wrong symbol instead of equals sign in DEVICES"""
    parser = new_parser(str(Path("test_files/test_parser1.2.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 6:\n\n"
        + "    SW1, SW2, SW3, SW4, SW5 - SWITCH(0);\n"
        + "                            ^\n\n"
        + "Expected '=' or ','\n"
        + "Error Count: 1\n"
    )


def test_parser_missing_dot(capfd):  # : instead of . in CONNECT
    """Wrong symbol instead of dot in CONNECT"""
    parser = new_parser(str(Path("test_files/test_parser1.3.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 19:\n\n"
        + "    SW2 > xor1:I2, nor1.I1;\n"
        + "              ^\n\n"
        + "Expected '.' or ',' or ';'\n"
        + "Error Count: 1\n"
    )


def test_parser_missing_arrow(capfd):  # = instead of > in CONNECT
    """Wrong symbol instead of > in CONNECT"""
    parser = new_parser(str(Path("test_files/test_parser1.4.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 33:\n\n"
        + "    dt1.QBAR = nand4.I1;\n"
        + "             ^\n\n"
        + "Expected '>'\n"
        + "Error Count: 1\n"
    )


def test_parser_missing_MONITOR(capfd):  # MONITOR misspelled
    """MONITOR misspelled"""
    parser = new_parser(str(Path("test_files/test_parser1.5.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 36:\n\n"
        + "MON1TOR\n"
        + "^\n\n"
        + "Expected 'MONITOR'\n"
        + "Error Count: 1\n"
    )


def test_parser_missing_close_brace(capfd):  # missing brace end of CONNECT
    """Missing right curly bracket at end of CONNECT"""
    parser = new_parser(str(Path("test_files/test_parser1.6.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 36:\n\n"
        + "MONITOR\n"
        + "^\n\n"
        + "Expected '}'\n"
        + "Error Count: 1\n"
    )


def test_parser_missing_open_brace(capfd):  # missing brace after CIRCUIT
    """Missing left curly bracket after CIRCUIT"""
    parser = new_parser(str(Path("test_files/test_parser1.7.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 4:\n\n"
        + "DEVICES\n"
        + "^\n\n"
        + "Expected '{'\n"
        + "Error Count: 1\n"
    )


def test_parser_missing_END(capfd):  # END misspelled
    """END misspelled"""
    parser = new_parser(str(Path("test_files/test_parser1.8.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 43:\n\n"
        + "EN\n"
        + "^\n\n"
        + "Expected 'END'\n"
        + "Error Count: 1\n"
    )


def test_parser_bad_name(capfd):  # 4SW4 as a name definition
    """Invalid name definition in DEVICES"""
    parser = new_parser(str(Path("test_files/test_parser1.9.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 6:\n\n"
        + "    SW1, SW2, SW3, 4SW4, SW5 = SWITCH(0);\n"
        + "                   ^\n\n"
        + "Device names must start with a letter and be alphanumeric\n"
        + "Error Count: 1\n"
    )


def test_parser_missing_semicolon(capfd):  # missing semicolon in MONITOR
    """Missing a semicolon in MONITOR"""
    parser = new_parser(str(Path("test_files/test_parser1.10.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 39:\n\n"
        + "}\n"
        + "^\n\n"
        + "Expected ';'\n"
        + "Error Count: 1\n"
    )


def test_parser_bad_clock_param(capfd):  # clock parameter is zero
    """Clock parameter is 0"""
    parser = new_parser(str(Path("test_files/test_parser1.11.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 12:\n\n"
        + "    CL1 = CLOCK(0);\n"
        + "                ^\n\n"
        + "Expected a number n > 0, the number of simulation cycles after"
        " which the state changes\n"
        + "Error Count: 1\n"
    )


def test_parser_bad_switch_param(capfd):  # switch parameter is two
    """Switch parameter is 2"""
    parser = new_parser(str(Path("test_files/test_parser1.12.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 6:\n\n"
        + "    SW1, SW2, SW3, SW4, SW5 = SWITCH(2);\n"
        + "                                     ^\n\n"
        + "Expected state, either 0(OFF) or 1(ON)\n"
        + "Error Count: 1\n"
    )


def test_parser_bad_gate_param_0(capfd):  # and gate parameter is 0
    """AND gate parameter is 0"""
    parser = new_parser(str(Path("test_files/test_parser1.13.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 11:\n\n"
        + "    and1 = AND(0);\n"
        + "               ^\n\n"
        + "Expected number of inputs for AND gate (valid range: 1-16)\n"
        + "Error Count: 1\n"
    )


def test_parser_bad_device_definition(capfd):  # errors in switch definition
    """Semicolon instead of comma in switch definition line"""
    parser = new_parser(str(Path("test_files/test_parser1.14.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 6:\n\n"
        + "    SW1; SWITCH2, SW3, SW4, SW5 = SWITCH(0);\n"
        + "       ^\n\n"
        + "Expected '=' or ','\n"
        + "Error Count: 1\n"
    )


def test_parser_xor_param(capfd):  # xor gate has a parameter
    """XOR gate has a parameter"""
    parser = new_parser(str(Path("test_files/test_parser1.15.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 9:\n\n" +
#             "    xor1, xor2 = XOR(2);\n" +
#             "                    ^\n\n" +
#             "Expected ';'\n" +
#             "Error Count: 1\n")


def test_parser_unsupported_device(capfd):  # declare unsupported device type
    """Declare an unsupported device type"""
    parser = new_parser(str(Path("test_files/test_parser1.16.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 14:\n\n"
        + "    inv1, inv2, inv3 = XNOR;\n"
        + "                       ^\n\n"
        + "Not a supported device, supported devices: CLOCK, SWITCH, AND,"
        " NAND, OR, NOR, DTYPE, XOR, NOT\n"
        + "Error Count: 1\n"
    )


def test_parser_no_gate_param1(capfd):  # forgot to initialise a gate parameter
    """No parentheses after a gate keyword"""
    parser = new_parser(str(Path("test_files/test_parser1.17.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 7:\n\n"
        + "    nand1, nand2, nand3, nand4 = NAND;\n"
        + "                                     ^\n\n"
        + "Expected '('\n"
        + "Error Count: 1\n"
    )


def test_parser_no_gate_param2(capfd):  # forgot to initialise a gate parameter
    """No number in parentheses after gate keyword"""
    parser = new_parser(str(Path("test_files/test_parser1.18.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 8:\n\n"
        + "    nor1, nor2 = NOR();\n"
        + "                     ^\n\n"
        + "Expected number of inputs for NOR gate (valid range: 1-16)\n"
        + "Error Count: 1\n"
    )


def test_parser_switch_param_is_01(capfd):  # switch parameter is 01
    """Switch parameter is (01)"""
    parser = new_parser(str(Path("test_files/test_parser1.19.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 6:\n\n"
        + "    SW1, SW2, SW3, SW4, SW5 = SWITCH(01);\n"
        + "                                      ^\n\n"
        + "Expected ')'\n"
        + "Error Count: 1\n"
    )


def test_parser_bad_pinname(capfd):  # and1 pinname is 1 instead of I1
    """Pinname is not a valid name"""
    parser = new_parser(str(Path("test_files/test_parser1.20.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 26:\n\n"
        + "    nor2 > and1.1, xor2.I1;\n"
        + "                ^\n\n"
        + "Pin names must start with a letter and be alphanumeric\n"
        + "Error Count: 1\n"
    )


def test_parser_multiple_errors():  # multiple minor syntax errors
    """Test parser can correctly count errors"""
    parser = new_parser(str(Path("test_files/test_parser1.21.txt")))
    assert parser.parse_network() == False
    assert parser.error_count == 18


def test_parser_bad_pinname(capfd):  # / instead of , in device definition
    """Wrong symbol instead of comma in device definition"""
    parser = new_parser(str(Path("test_files/test_parser1.22.txt")))
    assert parser.parse_network() == False
    out, _ = capfd.readouterr()
    assert (
        out
        == "\n\nError on line 7:\n\n"
        + "    nand1, nand2, nand3/ nand4 = NAND(2);\n"
        + "                       ^\n\n"
        + "Expected '=' or ','\n"
        + "Error Count: 1\n"
    )


def test_parser_no_semicolons():  # missing 3 final semicolons
    """Test parser gives 3 errors when missing final 3 semicolons"""
    parser = new_parser(str(Path("test_files/test_parser1.23.txt")))
    assert parser.parse_network() == False
    assert parser.error_count == 3


def test_parser_wrong_stop_symbol1(capfd):  # , instead of ; end of devices
    """Comma instead of semicolon at the end of devices"""
    parser = new_parser(str(Path("test_files/test_parser1.24.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 13:\n\n" +
#             "    dt1 = DTYPE,\n" +
#             "               ^\n\n" +
#             "Expected ';'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol2(capfd):  # , instead of ; end of connect
    """Comma instead of semicolon at the end of connect"""
    parser = new_parser(str(Path("test_files/test_parser1.25.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 33:\n\n" +
#             "    dt1.QBAR > nand4.I1,\n" +
#             "                       ^\n\n" +
#             "Expected ';'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol3(capfd):  # , instead of ; end of monitor
    """Comma instead of semicolon at the end of monitor"""
    parser = new_parser(str(Path("test_files/test_parser1.28.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 38:\n\n" +
#             "    xor2; nand4,\n" +
#             "               ^\n\n" +
#             "Expected ';'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol4():  # , instead of ; end of all
    """Comma instead of semicolon at the end of all 3 sections"""
    parser = new_parser(str(Path("test_files/test_parser1.29.txt")))
    assert parser.parse_network() == False


#     assert parser.error_count == 3


def test_parser_wrong_stop_symbol5():  # wrong symbol instead of ; end of all
    """Unknown symbols instead of semicolon at the end of all 3 sections"""
    parser = new_parser(str(Path("test_files/test_parser1.30.txt")))
    assert parser.parse_network() == False


#     assert parser.error_count == 3


def test_parser_wrong_stop_symbol6(capfd):  # , instead of ; middle of monitor
    """Comma instead of semicolon in the middle of monitor"""
    parser = new_parser(str(Path("test_files/test_parser1.31.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 38:\n\n" +
#             "    xor2, nand4;\n" +
#             "        ^\n\n" +
#             "Expected ';'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol7(capfd):  # / instead of } end of devices
    """Wrong symbol instead of right curly bracket at the end of devices"""
    parser = new_parser(str(Path("test_files/test_parser1.32.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 14:\n\n" +
#             "/\n" +
#             "^\n\n" +
#             "Expected '}'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol8(capfd):  # / instead of } end of connect
    """Wrong symbol instead of right curly bracket at the end of connect"""
    parser = new_parser(str(Path("test_files/test_parser1.33.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 34:\n\n" +
#             "/\n" +
#             "^\n\n" +
#             "Expected '}'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol9(capfd):  # / instead of } end of monitor
    """Wrong symbol instead of right curly bracket at the end of monitor"""
    parser = new_parser(str(Path("test_files/test_parser1.34.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 39:\n\n" +
#             "/\n" +
#             "^\n\n" +
#             "Expected '}'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol10(capfd):  # / instead of } end of circuit
    """Wrong symbol instead of right curly bracket at the end of circuit"""
    parser = new_parser(str(Path("test_files/test_parser1.35.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 41:\n\n" +
#             "/\n" +
#             "^\n\n" +
#             "Expected '}'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol11(capfd):  # / instead of { start of circuit
    """Wrong symbol instead of left curly bracket at the start of circuit"""
    parser = new_parser(str(Path("test_files/test_parser1.36.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 2:\n\n" +
#             "/\n" +
#             "^\n\n" +
#             "Expected '{'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol12(capfd):  # / instead of { start of devices
    """Wrong symbol instead of left curly bracket at the start of devices"""
    parser = new_parser(str(Path("test_files/test_parser1.37.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 5:\n\n" +
#             "/\n" +
#             "^\n\n" +
#             "Expected '{'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol13(capfd):  # / instead of { start of connect
    """Wrong symbol instead of left curly bracket at the start of connect"""
    parser = new_parser(str(Path("test_files/test_parser1.38.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 17:\n\n" +
#             "/\n" +
#             "^\n\n" +
#             "Expected '{'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol14(capfd):  # / instead of { start of monitor
    """Wrong symbol instead of left curly bracket at the start of monitor"""
    parser = new_parser(str(Path("test_files/test_parser1.39.txt")))
    assert parser.parse_network() == False


#     out, _ = capfd.readouterr()
#     assert (out == "\n\nError on line 37:\n\n" +
#             "/\n" +
#             "^\n\n" +
#             "Expected '{'\n" +
#             "Error Count: 1\n")


def test_parser_wrong_stop_symbol15():  # / instead of } all
    """Wrong symbol instead of right curly bracket at the end of all"""
    parser = new_parser(str(Path("test_files/test_parser1.40.txt")))
    assert parser.parse_network() == False


#     assert parser.error_count == 4


def test_parser_wrong_stop_symbol16():  # / instead of { all
    """Wrong symbol instead of left curly bracket at the start of all"""
    parser = new_parser(str(Path("test_files/test_parser1.41.txt")))
    assert parser.parse_network() == False


#     assert parser.error_count == 4


def test_parser_wrong_stop_symbol17():  # / instead of { circuit and devices
    """/ instead of { at start of circuit and missing { at start of devices"""
    parser = new_parser(str(Path("test_files/test_parser1.42.txt")))
    assert parser.parse_network() == False


#     assert parser.error_count == 2


def test_parser_wrong_stop_symbol18():  # / instead of { circuit and devices
    """/ instead of { at start of circuit and devices"""
    parser = new_parser(str(Path("test_files/test_parser1.43.txt")))
    assert parser.parse_network() == False


#     assert parser.error_count == 2


def test_parser_no_keywords():  # missing CIRCUIT, DEVICES etc
    """Missing all keywords in file"""
    parser = new_parser(str(Path("test_files/test_parser1.26.txt")))
    assert parser.parse_network() == False
    assert parser.error_count == 5


def test_parser_no_right_brace():  # missing all right braces
    """Missing all right braces in file"""
    parser = new_parser(str(Path("test_files/test_parser1.27.txt")))
    assert parser.parse_network() == False
    assert parser.error_count == 4


def test_empty_file():
    """Test parser can handle an empty file"""
    parser = new_parser(str(Path("test_files/test_parser1.44.txt")))
    assert parser.parse_network() == False


def test_parser_input_to_input(capfd):
    """Semantic error input connected to input"""
    parser = new_parser(str(Path("test_files/test_parser2.1.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 22:\n\n    or1.I1 > nand1.I2;\n                 "
        "  ^\n\nInput already connected\nError Count: 1\n"
    )


def test_parser_output_to_output(capfd):
    """Semantic error output connected to output"""
    parser = new_parser(str(Path("test_files/test_parser2.2.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 21:\n\n    xor1 > nand1.I1, nor1;\n        "
        " ^\n\nOutput connected to output\nError Count: 1\n"
    )


def test_parser_input_not_connected(capfd):
    """Semantic error input not connected"""
    parser = new_parser(str(Path("test_files/test_parser2.3.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 16:\n\nCONNECT\n^\n\nunconnected inputs:"
        " nand3.I1 xor2.I1 \nError Count: 1\n"
    )


def test_parser_multiple_connections_to_input(capfd):
    """Semantic error multiple connections to input"""
    parser = new_parser(str(Path("test_files/test_parser2.4.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 28:\n\n    and1 > dt1.DATA, nand2.I1;\n         "
        "                  ^\n\nInput already connected\nError Count: 1\n"
    )


def test_parser_devicename_not_found(capfd):
    """Semantic error reference undeclared device"""
    parser = new_parser(str(Path("test_files/test_parser2.5.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 18:\n\n    SW1 > xor1.I1, or1.I1;\n         "
        " ^\n\nSpecified device does not exist\nError Count: 1\n"
    )


def test_parser_pinname_not_found(capfd):
    """Semantic error reference pinname I3 but gate only has 2 inputs"""
    parser = new_parser(str(Path("test_files/test_parser2.6.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 27:\n\n    nand3 > and1.I3, nand4.I2;\n         "
        "        ^\n\nSpecified port does not exist\nError Count: 1\n"
    )


def test_parser_too_many_inputs(capfd):
    """Semantic error and gate has 17 inputs"""
    parser = new_parser(str(Path("test_files/test_parser2.7.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 11:\n\n    and1 = AND(17);\n              "
        " ^\n\nNumber of inputs must be between 1-16\nError Count: 1\n"
    )


def test_parser_devicename_keyword(capfd):
    """Semantic error devicename should not be keyword"""
    parser = new_parser(str(Path("test_files/test_parser2.8.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 13:\n\n    DEVICES = DTYPE;\n    ^\n\nNames"
        " cannot"
        " be Keywords: 'CIRCUIT', 'DEVICES', 'CONNECT', 'MONITOR',"
        " 'END','CLOCK', 'SWITCH', 'AND', 'NAND', 'OR', 'NOR', 'XOR',"
        " 'NOT', 'DTYPE'\nError Count: 1\n"
    )


def test_parser_pinname_keyword(capfd):
    """Semantic error pinname should not be keyword"""
    parser = new_parser(str(Path("test_files/test_parser2.9.txt")))
    assert not parser.parse_network()
    output = capfd.readouterr()[0]
    assert (
        output
        == "\n\nError on line 31:\n\n    SW5 > dt1.CONNECT;\n             "
        " ^\n\nNames cannot be Keywords: 'CIRCUIT', 'DEVICES', 'CONNECT',"
        " 'MONITOR', 'END','CLOCK', 'SWITCH', 'AND', 'NAND', 'OR', 'NOR',"
        " 'XOR', 'NOT', 'DTYPE'\nError Count: 1\n"
    )


def test_parser_semantic_semantic(capfd):
    """Test parser continues after semantic error"""
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
        " 'SWITCH', 'AND', 'NAND', 'OR', 'NOR', 'XOR', 'NOT', 'DTYPE'\nError"
        " Count: 2\n"
    )


def test_parser_semantic_semantic2(capfd):
    """Test parser only finds first of 2 semantic errors"""
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
    """Test parser finds syntax error after semantic error"""
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
    """Test parser doesn't find semantic error after syntax error"""
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
