import csv
import gdb


class variable:
    """Data structure to store metadata and values of a variable
    during GDB execution.
    """

    def __init__(self, name, python_type, dimension):
        """Initialize with metadata

        :param name: name of the variable in the symbol table
        :param python_type: target python type for conversion
        :param dimension: array dimensions of Fortran variable as tuple

        Examples
        --------
        Scalar integer: python_type = 'int', dimension = (1,)
        1D float array: python_type = 'float', dimension = (3,)
        2D float array: python_type = 'float', dimension = (3,2)

        """

        self.name = name
        self.dimension = dimension
        self.data = []

        if python_type not in ['int', 'float']:
            raise NotImplementedError('Target type unsupported!')
        else:
            self.python_type = python_type

    def cast(self, value):
        """Perform type conversion from gdb.Value.
        """

        if self.python_type == 'int':
            return int(value)
        elif self.python_type == 'float':
            return float(value)

    def append(self):
        """Append the given gdb_value to self.data after type conversion.
        For anything except scalar data, nested lists are used.

        Notes
        -----
        Using numpy would be much better, but I need to maintain compatibility
        with the Intel GDB which sadly has no numpy available in it's
        embedded Python interpreter.

        """

        if self.dimension == (1,):
            # Scalar data is trivially handled
            self.data.append(self.cast(gdb.parse_and_eval(self.name)))
        elif len(self.dimension) == 1 and self.dimension > (1,):
            # For one dimensional arrays, we use lists of lists
            self.data.append([self.cast(gdb.parse_and_eval(self.name)[i])
                              # Start indexing from 1 for Fortran variables
                              for i in range(1, self.dimension[0]+1)])
        else:
            raise NotImplementedError('Multidimensional arrays unsupported!')


# Define breakpoint line
b_line = '10'

# Define variables for collection
my_variables = {
    'i': variable(name='i', python_type='int', dimension=(1,)),
    'res': variable(name='res', python_type='int', dimension=(2,)),
}

# Set breakpoint
gdb.Breakpoint(b_line)

# Global boolean to control loop execution in collect()
loop = False


def exit_handler(event):
    """This is called if the inferior exits in GDB. It sets the global boolean
    loop to False to stop the loop that continues execution and collects the
    variables.

    :param event: GDB event

    """
    global loop
    if (isinstance(event, gdb.ExitedEvent)):
        loop = False


# Connect exit_handler to events.exited
gdb.events.exited.connect(exit_handler)


def collect():
    """Calling this from GDB via 'py collect()' will make GDB run the program
    and continue execution after hitting any breakpoint until loop is set to
    False.
    During the execution, it collects the data of all variables defined in
    my_variables every time a breakpoint is hit.

    """

    global loop

    # Reset global loop stopper
    loop = True

    # Run
    gdb.execute('r')

    while loop:
        # Fetch values
        for v in my_variables.values():
            v.append()

        # Move to next breakpoint
        gdb.execute('c')

    # Print data
    for key, v in my_variables.items():
        print(key, v.data)


def export():
    """Calling this from GDB via 'py export()' will write all variable data
    in my_variables to CSV files for plotting.

    """

    delim = ','

    for key, v in my_variables.items():
        with open('{}_gdbc.csv'.format(key), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=delim)

            # Write header
            if v.dimension == (1,):
                writer.writerow(
                    ['# breakpoint hit', key]
                )
            elif len(v.dimension) == 1 and v.dimension > (1,):
                writer.writerow(
                    ['# breakpoint hit'] +
                    # Start indexin with zero here
                    ['{}[{}]'.format(key, i) for i in range(v.dimension[0])]
                )
            else:
                raise NotImplementedError(
                    'Multidimensional arrays unsupported!')

            # Write data rows
            if v.dimension == (1,):
                for i in range(len(v.data)):
                    writer.writerow(
                        ['{}'.format(i)] +
                        ['{}'.format(v.data[i])]
                    )
            elif len(v.dimension) == 1 and v.dimension > (1,):
                for i in range(len(v.data)):
                    writer.writerow(
                        ['{}'.format(i)] +
                        ['{}'.format(v.data[i][j])
                         for j in range(v.dimension[0])]
                    )
            else:
                raise NotImplementedError(
                    'Multidimensional arrays unsupported!')
