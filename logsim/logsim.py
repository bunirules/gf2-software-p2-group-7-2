#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys

import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from translate import Translator
from userint import UserInterface
from gui import Gui


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = (
        "Usage:\n"
        "Show help: logsim.py -h\n"
        "Command line user interface: logsim.py -c <file path>\n"
        "Graphical user interface: logsim.py"
    )
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif (
            option == "-c" and len(arguments) <= 1
        ):  # use the command line user interface
            if len(arguments) == 1:
                [lang] = arguments
                translator = Translator(lang=lang)
            else:
                translator = Translator()
            scanner = Scanner(path, names)
            parser = Parser(
                names, devices, network, monitors, scanner, translator
            )
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()

    if not options:  # no option given, use the graphical user interface

        if len(arguments) <= 1:  # no argument or language choice
            if len(arguments) == 1:
                [lang] = arguments
                translator = Translator(lang=lang)
            else:
                translator = Translator()
            app = wx.App()
            gui = Gui("Logic Simulator", "", names, devices, network, monitors)
            app.MainLoop()
        elif len(arguments) > 1:  # too many arguments
            print(
                "Error: When using GUI, do not give any arguments except"
                " optional language ID.\n"
            )
            print(usage_message)
            sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
