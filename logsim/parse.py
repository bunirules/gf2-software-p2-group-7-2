"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

import sys
from scanner import Symbol


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.
    language: language to use

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.

    Private methods
    --------------
    __circuit(self): Parse circuit syntax.

    __devicelist(self): Parse list of device

    __device(self): Parse device definition

    __devicename(self): Parse name of device

    __name(self, type): Parse a name

    __clock(self): Parse CLOCK definition

    __switch(self): Parse SWITCH definition

    __And(self): Parse AND definition

    __nand(self): Parse NAND definition 

    __nor(self): Parse NOR definition 

    __oor(self): Parse OR definition 

    __connectionlist(self): Parse list of connections

    __con(self): Parse a conncection

    __point(self): Parse a point

    __pinname(self): Parse a pin name

    __monitorlist(self): Parse a list of monitors

    __monitor(self): Parse a monitor

    __error(self, message, stopping_symbol=";", symbol=None): Produce an error message
    """

    def __init__(self, names, devices, network, monitors, scanner, translator):
        """Initialise constants."""
        self.__names = names
        self.__devices = devices
        self.network = network
        self.__monitors = monitors
        self.scanner = scanner
        self.translator = translator
        self.symbol = self.scanner.get_symbol()
        self.error_ = False
        self.error_count = 0
        self.skip = False
        self.cur_attribute = None
        self.error_msg = ""

    def parse_network(self):
        """Parse the circuit definition file."""
        self.__circuit()
        if (
            self.symbol.type == self.scanner.KEYWORD
            and self.symbol.id == self.scanner.END_ID
        ):
            self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected 'END'")
        self.error_msg += "\n\n" + f"Error Count: {self.error_count}"
        print(f"Error Count: {self.error_count}")
        return not self.error_

    def __circuit(self):
        """Parse circuit syntax."""
        if (
            self.symbol.type == self.scanner.KEYWORD
            and self.symbol.id == self.scanner.CIRCUIT_ID
        ):
            self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected 'CIRCUIT'", "{")
        if self.symbol.type == self.scanner.BRACE_LEFT:
            self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected '{'", None)

        self.__devicelist()
        self.__connectionlist()
        self.__monitorlist()
        if self.symbol.type == self.scanner.BRACE_RIGHT:
            self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected '}'", None)

    def __devicelist(self):
        """Parse device list syntax."""
        right_brace = True
        if (
            self.symbol.type == self.scanner.KEYWORD
            and self.symbol.id == self.scanner.DEVICES_ID
        ):
            self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected 'DEVICES'", "{")
        if self.symbol.type == self.scanner.BRACE_LEFT:
            self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected '{'", None)

        self.__device()
        while (
            self.symbol.type != self.scanner.BRACE_RIGHT
            and self.symbol.type != self.scanner.EOF
        ):
            # Check for CONNECT to detect missing right brace
            if self.symbol.id == self.scanner.CONNECT_ID:
                self.check_symbol = self.scanner.get_symbol()
                if self.check_symbol.type == self.scanner.BRACE_LEFT:
                    self.skip = True
                    self.__error("Expected '}'", None)
                    self.symbol = self.check_symbol
                    right_brace = False
                    break
                # Or used CONNECT as name
                else:
                    self.__error(
                        "Device names cannot be Keywords: 'CIRCUIT',"
                        " 'DEVICES', 'CONNECT', 'MONITOR', 'END','CLOCK',"
                        " 'SWITCH', 'AND', 'NAND', 'OR', 'NOR', 'XOR', 'NOT' 'DTYPE'"
                    )
                    self.symbol = self.scanner.get_symbol()

            self.__device()
        if right_brace:
            self.symbol = self.scanner.get_symbol()

    def __device(self):
        """Parse device syntax."""
        self.cur_device_name_list = []
        if self.__devicename():
            valid_device_list = True
            while (
                self.symbol.type == self.scanner.COMMA
                and self.symbol.type != self.scanner.EOF
                and valid_device_list
            ):
                self.symbol = self.scanner.get_symbol()
                valid_device_list = self.__devicename()
            if valid_device_list:
                if self.symbol.type == self.scanner.EQUALS:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.id == self.scanner.CLOCK_ID:
                        self.symbol = self.scanner.get_symbol()
                        self.__clock()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_clock(
                                    device_id, self.cur_attribute
                                )
                    elif self.symbol.id == self.scanner.SWITCH_ID:
                        self.symbol = self.scanner.get_symbol()
                        self.__switch()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_switch(
                                    device_id, self.cur_attribute
                                )
                    elif self.symbol.id == self.scanner.AND_ID:
                        self.symbol = self.scanner.get_symbol()
                        self.__And()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_gate(
                                    device_id,
                                    self.__devices.AND,
                                    self.cur_attribute,
                                )
                    elif self.symbol.id == self.scanner.NAND_ID:
                        self.symbol = self.scanner.get_symbol()
                        self.__nand()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_gate(
                                    device_id,
                                    self.__devices.NAND,
                                    self.cur_attribute,
                                )
                    elif self.symbol.id == self.scanner.OR_ID:
                        self.symbol = self.scanner.get_symbol()
                        self.__oor()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_gate(
                                    device_id,
                                    self.__devices.OR,
                                    self.cur_attribute,
                                )
                    elif self.symbol.id == self.scanner.NOR_ID:
                        self.symbol = self.scanner.get_symbol()
                        self.__nor()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_gate(
                                    device_id,
                                    self.__devices.NOR,
                                    self.cur_attribute,
                                )
                    elif self.symbol.id == self.scanner.DTYPE_ID:
                        self.symbol = self.scanner.get_symbol()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_d_type(device_id)
                    elif self.symbol.id == self.scanner.XOR_ID:
                        self.symbol = self.scanner.get_symbol()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_gate(
                                    device_id, self.__devices.XOR, 2
                                )
                    elif self.symbol.id == self.scanner.NOT_ID:
                        self.symbol = self.scanner.get_symbol()
                        if not self.error_:
                            device_ids = self.__names.lookup(
                                [
                                    dev.string
                                    for dev in self.cur_device_name_list
                                ]
                            )
                            for device_id in device_ids:
                                self.__devices.make_gate(
                                    device_id, self.__devices.NOT, 1
                                )
                    else:
                        self.__error(
                            "Not a supported device, supported devices: CLOCK,"
                            " SWITCH, AND, NAND, OR, NOR, DTYPE, XOR, NOT"
                        )
                else:
                    self.__error("Expected '=' or ','")

        if self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected ';'", None)

    def __devicename(self):
        """Parse device name.

        Returns:
            Bool: Device name conforms to syntax.
        """
        return self.__name("devicename")

    def __name(self, type):
        """Parse name.

        Args:
            type (string): Specifies if name is for a device or for a pin

        Returns:
            Bool: Name conforms to syntax.
        """
        if self.symbol.type == self.scanner.NAME:
            if type == "devicename":
                if not self.error_:
                    self.cur_device_name_list.append(self.symbol)
            if type == "pinname":
                if not self.error_:
                    self.cur_pin_name_list.append(self.symbol)
            self.symbol = self.scanner.get_symbol()
            return True
        elif self.symbol.type == self.scanner.KEYWORD:
            self.__error(
                "Names cannot be Keywords: 'CIRCUIT', 'DEVICES', 'CONNECT',"
                " 'MONITOR', 'END','CLOCK', 'SWITCH', 'AND', 'NAND', 'OR',"
                " 'NOR', 'XOR', 'NOT', 'DTYPE'"
            )
        else:
            if type == "devicename":
                self.__error(
                    "Device names must start with a letter and be alphanumeric"
                )
            elif type == "pinname":
                self.__error(
                    "Pin names must start with a letter and be alphanumeric"
                )
            return False

    def __clock(self):
        """Parse clock definition."""
        if self.symbol.type == self.scanner.PARENTHESIS_LEFT:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NUMBER:
                num = int(self.symbol.string)
                if num <= 0:
                    self.__error("Clock half period must be greater than 0")
                    self.skip = True
                if not self.error_:
                    self.cur_attribute = num
                if not self.skip:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.PARENTHESIS_RIGHT:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.__error("Expected ')'")
                self.skip = False
            else:
                self.__error(
                    "Expected a number n > 0, the number of simulation cycles"
                    " after which the state changes"
                )
        else:
            self.__error("Expected '('")

    def __switch(self):
        """Parse switch definition."""
        if self.symbol.type == self.scanner.PARENTHESIS_LEFT:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id == 0 or self.symbol.id == 1:
                if not self.error_:
                    self.cur_attribute = self.symbol.id
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.PARENTHESIS_RIGHT:
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.__error("Expected ')'")
            else:
                self.__error("Expected state, either 0(OFF) or 1(ON)")
        else:
            self.__error("Expected '('")

    def __And(self):
        """Parse AND gate defintion."""
        if self.symbol.type == self.scanner.PARENTHESIS_LEFT:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NUMBER:
                num = int(self.symbol.string)
                if not (0 < num and num <= 16):
                    self.skip = True
                    self.__error("Number of inputs must be between 1-16")
                if not self.error_:
                    self.cur_attribute = num
                if not self.skip:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.PARENTHESIS_RIGHT:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.__error("Expected ')'")
                self.skip = False
            else:
                self.__error(
                    "Expected number of inputs for AND gate (valid range:"
                    " 1-16)"
                )
        else:
            self.__error("Expected '('")

    def __nand(self):
        """Parse NAND gate definiton."""
        if self.symbol.type == self.scanner.PARENTHESIS_LEFT:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NUMBER:
                num = int(self.symbol.string)
                if not (0 < num and num <= 16):
                    self.skip = True
                    self.__error("Number of inputs must be between 1-16")
                if not self.error_:
                    self.cur_attribute = num
                if not self.skip:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.PARENTHESIS_RIGHT:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.__error("Expected ')'")
                self.skip = False
            else:
                self.__error(
                    "Expected number of inputs for NAND gate (valid range:"
                    " 1-16)"
                )
        else:
            self.__error("Expected '('")

    def __nor(self):
        """Parse NOR gate definition."""
        if self.symbol.type == self.scanner.PARENTHESIS_LEFT:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NUMBER:
                num = int(self.symbol.string)
                if not (0 < num and num <= 16):
                    self.skip = True
                    self.__error("Number of inputs must be between 1-16")
                if not self.error_:
                    self.cur_attribute = num
                if not self.skip:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.PARENTHESIS_RIGHT:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.__error("Expected ')'")
                self.skip = False
            else:
                self.__error(
                    "Expected number of inputs for NOR gate (valid range:"
                    " 1-16)"
                )
        else:
            self.__error("Expected '('")

    def __oor(self):
        """Parse OR gate definition."""
        if self.symbol.type == self.scanner.PARENTHESIS_LEFT:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NUMBER:
                num = int(self.symbol.string)
                if not (0 < num and num <= 16):
                    self.skip = True
                    self.__error("Number of inputs must be between 1-16")
                if not self.error_:
                    self.cur_attribute = num
                if not self.skip:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.PARENTHESIS_RIGHT:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.__error("Expected ')'")
                self.skip = False
            else:
                self.__error(
                    "Expected number of inputs for OR gate (valid range: 1-16)"
                )
        else:
            self.__error("Expected '('")

    def __connectionlist(self):
        """Parse connection list."""
        connect_Symbol = self.symbol
        right_brace = True
        if not self.skip:
            if (
                self.symbol.type == self.scanner.KEYWORD
                and self.symbol.id == self.scanner.CONNECT_ID
            ):
                self.symbol = self.scanner.get_symbol()
            else:
                self.__error("Expected 'CONNECT'", "{")
        self.skip = False

        if self.symbol.type == self.scanner.BRACE_LEFT:
            self.symbol = self.scanner.get_symbol()

        else:
            self.__error("Expected '{'", None)

        self.__con()

        while (
            self.symbol.type != self.scanner.BRACE_RIGHT
            and self.symbol.type != self.scanner.EOF
        ):
            # Check for MONITOR to detect missing right brace
            if self.symbol.id == self.scanner.MONITOR_ID:
                self.check_symbol = self.scanner.get_symbol()
                # Checks for right brace to detect missing semi-colon
                if self.check_symbol.type == self.scanner.BRACE_LEFT:
                    self.skip = True
                    self.__error("Expected '}'", None)
                    self.symbol = self.check_symbol
                    right_brace = False
                    break
                # Or use of MONITOR as device name
                else:
                    self.__error(
                        "Device names cannot be Keywords: 'CIRCUIT',"
                        " 'DEVICES', 'CONNECT', 'MONITOR', 'END','CLOCK',"
                        " 'SWITCH', 'AND', 'NAND', 'OR', 'NOR', 'XOR', 'NOT' 'DTYPE'"
                    )
                    self.symbol = self.scanner.get_symbol()

            self.__con()

        if not self.error_:
            unconnected = self.network.check_network()
            if not unconnected == "":
                self.__error(
                    "unconnected inputs: " + unconnected, None, connect_Symbol
                )

        if right_brace:
            self.symbol = self.scanner.get_symbol()

    def __con(self):
        """Parse connection."""
        self.cur_device_name_list = []
        self.cur_pin_name_list = []
        if self.__point():
            if not self.error_:
                out_device_sym = self.cur_device_name_list[0]
                out_pin_sym = self.cur_pin_name_list[0]
                out_device_id = self.__names.query(out_device_sym.string)
                out_pin_id = self.__names.query(out_pin_sym.string)
                self.cur_device_name_list = []
                self.cur_pin_name_list = []
            if self.symbol.type == self.scanner.ARROW:
                self.cur_arrow = self.symbol
                self.symbol = self.scanner.get_symbol()
                self.__point()
                while (
                    self.symbol.type == self.scanner.COMMA
                    and self.symbol.type != self.scanner.EOF
                ):
                    self.symbol = self.scanner.get_symbol()
                    self.__point()

                if self.symbol.type != self.scanner.SEMICOLON:
                    # Checks for right brace to detect missing semi-colon
                    if self.symbol.type == self.scanner.BRACE_RIGHT:
                        self.skip = True
                        self.__error("Expected ';'", None)
                    else:
                        self.__error("Expected '.' or ',' or ';'")
            else:
                self.__error("Expected '>'")

        if not self.error_:
            cur_in_device_ids = [
                self.__names.query(dev.string)
                for dev in self.cur_device_name_list
            ]
            cur_in_pin_ids = [
                self.__names.query(dev.string) for dev in self.cur_pin_name_list
            ]

            for i in range(len(cur_in_device_ids)):
                in_dev_id = cur_in_device_ids[i]
                in_pin_id = cur_in_pin_ids[i]
                error = self.network.make_connection(
                    out_device_id, out_pin_id, in_dev_id, in_pin_id
                )
                if error != self.network.NO_ERROR:
                    if (
                        error == self.network.INPUT_CONNECTED
                        or error == self.network.PORT_ABSENT_2
                    ):
                        self.__error(
                            self.network.error_message[error],
                            None,
                            self.cur_pin_name_list[i],
                        )
                    elif error == self.network.DEVICE_ABSENT_2:
                        self.__error(
                            self.network.error_message[error],
                            None,
                            self.cur_device_name_list[i],
                        )
                    elif error == self.network.DEVICE_ABSENT_1:
                        self.__error(
                            self.network.error_message[error],
                            None,
                            out_device_sym,
                        )
                    elif error == self.network.PORT_ABSENT_1:
                        self.__error(
                            self.network.error_message[error],
                            None,
                            out_pin_sym,
                        )
                    else:
                        self.__error(
                            self.network.error_message[error],
                            None,
                            self.cur_arrow,
                        )
                    break
        if not self.skip:
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.__error("Expected ';'", None)
        self.skip = False

    def __point(self):
        """Parse point definition.

        Returns:
            Bool: Point conforms to syntax.
        """
        if self.__devicename():
            if self.symbol.type == self.scanner.DOT:
                self.symbol = self.scanner.get_symbol()
                return self.__pinname()
            else:
                symb = Symbol()
                symb.string = None
                self.cur_pin_name_list.append(symb)
            return True
        else:
            return False

    def __pinname(self):
        """Parse pin name.

        Returns:
            Bool: Name conforms to syntax.
        """
        return self.__name("pinname")

    def __monitorlist(self):
        """Parse monitor list."""
        right_brace = True
        if not self.skip:
            if (
                self.symbol.type == self.scanner.KEYWORD
                and self.symbol.id == self.scanner.MONITOR_ID
            ):
                self.symbol = self.scanner.get_symbol()
            else:
                self.__error("Expected 'MONITOR'", "{")
        self.skip = False

        if self.symbol.type == self.scanner.BRACE_LEFT:
            self.symbol = self.scanner.get_symbol()
            self.__monitor()

            while (
                self.symbol.type != self.scanner.BRACE_RIGHT
                and self.symbol.type != self.scanner.EOF
            ):
                # Checks for END to detect missing right braces
                if self.symbol.id == self.scanner.END_ID:
                    self.__error("Expected '}'", None)
                    right_brace = False
                    break
                self.__monitor()
            if right_brace:
                self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected '{'", None)

    def __monitor(self):
        """Parse monitor definition."""
        self.cur_device_name_list = []
        self.cur_pin_name_list = []
        self.__point()
        if not self.error_:
            error = self.__monitors.make_monitor(
                self.__names.query(self.cur_device_name_list[0].string),
                self.__names.query(self.cur_pin_name_list[0].string),
            )
            if error != self.__monitors.NO_ERROR:
                self.__error(self.__monitors.error_message[error], None)
        if self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
        else:
            self.__error("Expected ';'", None)

    def __error(self, message, stopping_symbol=";", symbol=None):
        """Generate error message, update error counter, set error state.

        Args:
            message (str): error message for printing
            stopping_symbol (str): Stopping symbol to resume parsing from.
            Defaults to ";".
            symbol (symbol object): error symbol object passed to scanner
            for error message construction. Defaults to None.

        Returns:
            str: error message.
        """
        if symbol is None:
            symbol = self.symbol
        self.error_ = True
        self.error_count += 1
        error_output = self.scanner.print_error(symbol, message)
        if stopping_symbol is not None:
            while (
                self.symbol.string != stopping_symbol
                and self.symbol.type != self.scanner.EOF
            ):
                self.symbol = self.scanner.get_symbol()

        self.error_msg += "\n\n" + error_output

        return error_output
