"""Implements a name table for lexical analysis.

Classes
-------
MyNames - implements a name table for lexical analysis.
"""


class MyNames:

    """Implements a name table for lexical analysis.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    lookup(self, name_string): Returns the corresponding name ID for the
                 given name string. Adds the name if not already present.

    get_string(self, name_id): Returns the corresponding name string for the
                 given name ID. Returns None if the ID is not a valid index.
    """

    def __init__(self):
        """Initialise the names list."""
        self.names_list = []

    def lookup(self, name_string):
        """Return the corresponding name ID for the given name_string.

        If the name string is not present in the names list, add it.
        """
        if name_string in self.names_list:
            return self.names_list.index(name_string)
        else:
            self.names_list.append(name_string)
            return len(self.names_list) - 1

    def get_string(self, name_id):
        """Return the corresponding name string for the given name_id.

        If the name ID is not a valid index into the names list, return None.
        """
        if type(name_id) == str:
            if not name_id.isnumeric():
                print("String ID must be an integer" )
                raise TypeError
            name_id = float(name_id)
        if name_id%1 != 0:
            print('String ID must be an integer')
            raise TypeError
        name_id = int(name_id)
        if name_id < 0:
            print("String ID cannot be negative")
            raise ValueError
        elif name_id >= len(self.names_list):
            print("String ID too large")
            return None
        else:
            return self.names_list[name_id]
