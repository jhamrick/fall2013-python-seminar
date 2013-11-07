# Homework 8: Parallelization

Jessica Hamrick  
jhamrick@berkeley.edu

All of the code for this week is in the notebook
`parallelization.ipynb`. It defines four different methods for
computing the Monte Carlo estimate of $\pi$:

* Simple serial method using Python builtin libraries
* Multiprocessing method, which splits the simple method across
  multiple processes
* IPython cluster method, which splits the simple method across
  multiple engines
* Numpy serial method utilizing fast array computation

Running the notebook will test all of these methods, and then
procedurally run these methods several times (10 runs each) for
different sample sizes (8, 48, 216, 1000, 4640, 21544, 100000, 464160,
2154436, 10000000). It then plots the median and confidence intervals
corresponding to one standard deviation above and below the 50th
percentile (I think this is better than centering around the mean for
timing, because occasionally you get outliers due to unrelated
computations, which can skew the estimate).

The plot shows that for this particular type of simulation, numpy is
actually much faster than the simple pure-Python implementation, even
when the simple method is parallelized. This is probably a combination
of three reasons: one, numpy is a compiled library that is highly
optimized for exactly these types of computations; two, native Python
function calls are fairly slow (and the simple solution makes $O(n)$
*Python* function calls, whereas numpy makes $O(1)$); and three, numpy
also already makes some use of parallelization. Multiprocessing and
the IPython cluster come in second and are fairly close in
performance, though the IPython cluster slightly outperforms the
multiprocessing library.

These simulations were run on my Macbook Air (which has a 2 GHz Intel
Core i7 processor, i.e. 2 cores).
