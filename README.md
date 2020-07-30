### Overview
TP-ELC is a robot manipulator model. This code includes emulation its several
functions. At all, the project not aimed to work with the robot as much, as
to solve applied task - show by a simplest example how genetic algorithms
works. So, the emulator is one of the methods of demonstrating the operation
of the algorithm. You can load generated control files inside the manipulator.
But, I didn't do it and don't know sequencing for this, including an exact
working field size (and its cell size) of the your model (partly, that's why
you can set your own sizes).

Genetic algorithms sometimes used to search approximate solutions of
non-polynomial problems. Actually, `gen.py` is looking for a solution one
such problem: arrange elements on a printed circuit board so, that the total
length of the links of the scheme is minimal (by the way, besides this problem
there is one more - wire tracing between PCB's elements). In fact, the scheme
is just digraph, where elements is vertices, and wires - edges. In loosely
coupled schemes it's not difficult. But, when the scheme consists of a large
number of elements and has a high connectedness coefficient - the task becomes
much more difficult. `gen.py` is a simplets genetic algorithm to solve this
problem, and `emulator.py` is a tool to display the result.

### Usage
The next command:

`./gen.py 12 40 20 13 25 20 6 100 data`

looking for the optimal placement for a `12`-element circuit. A working field
size is `13` units by X and `25` units by Y. Cell size is `40` and `20`.
Thereby, a relative size of the working field is 520 units by X and 500 units
by Y. Number of wires (edges) in the scheme is `20`. And, maximum wires
between two elements is `6`. `100` - is a quantity of permutations
(iterations) of the scheme elements (you can customize its mechanism, using
optional flags or expanding the program functionality). `data` - is a control
file name. Don't worry: as you might have noticed - the key arguments is
positional. Furthermore, you can always call help (e. g., by running the
command without arguments).

`./emulator.py 12 40 20 13 25 data`

The emulator looks at the generated control file (that you created with the
command above) and use it to display the placement result. For now, the
program needs data on the number of elements, a working field size and a
cell size (in principle, I could move this to the control file, but I think,
that it isn't comfortable).
