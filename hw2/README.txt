CalCalc Module
==============

Jessica Hamrick (jhamrick@berkeley.edu)

The CalCalc module provides a simple calculator. For more complex
calculations, it attempts to ask WolframAlpha. If the simple Python
evaluation fails, the program will print a warning that it is asking
WolframAlpha, just to be completely explicit.

Installation
------------

From the command line, run:

$ python setup.py install


Usage
-----

CalCalc can be run either from the command line, or from the
interpreter. From the command line:

$ python CalCalc.py "2+2"
4

$ python CalCalc.py "mass of the moon in kg"
CalCalc.py:122: UserWarning: Python evaluation failed, asking Wolfram Alpha
  warnings.warn("Python evaluation failed, asking Wolfram Alpha")
7.3459×10^22 kg  (kilograms)

$ python CalCalc.py -f "mass of the moon in kg"
CalCalc.py:122: UserWarning: Python evaluation failed, asking Wolfram Alpha
  warnings.warn("Python evaluation failed, asking Wolfram Alpha")
7.3459e+22  (kilograms)

From the Python interpreter:

>>> from CalCalc import calculate
>>> calculate("2+2")
4
>>> calculate("mass of the moon in kg")
CalCalc.py:122: UserWarning: Python evaluation failed, asking Wolfram Alpha
  warnings.warn("Python evaluation failed, asking Wolfram Alpha")
'7.3459x10^22 kg  (kilograms)'
>>> calculate("mass of the moon in kg", return_float=True)
7.3459e+22


Testing
-------

You can run the test suite using nose:

$ nosetests CalCalc.py
