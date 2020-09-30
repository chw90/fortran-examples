This example uses GDB's integrated python interpreter to collect the values of Fortran variables during debugging and export them in a CSV file.

It supports scalars or one-dimensional arrays of integers or floats.

Compile with gfortran and start GDB:

```bash
$ gfortran -g -O0 -o gdb_example gdb_example.f90
$ gdb gdb_example
```

In the GDB session, source the Python script:

```GDB
(gdb) source gdb_collect.py
(gdb) py collect()
(gdb) py export()
```

Check out the generated `i_gdb.csv` and `res_gdbc.csv` files.

Visualizing the evolution of variables during execution is now easy using gnuplot:

```bash
$ gnuplot
```

```Gnuplot
gnuplot> set datafile separator ","
gnuplot> set autoscale
gnuplot> plot "res_gdbc.csv" using 1:3
```