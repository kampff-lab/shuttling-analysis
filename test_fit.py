# -*- coding: utf-8 -*-
"""
Created on Tue May 14 20:25:11 2013

@author: IntelligentSystems
"""

import numpy
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def _polynomial(x, *p):
    """Polynomial fitting function of arbitrary degree."""
    poly = 0.
    for i, n in enumerate(p):
        poly += n * x**i
    return poly

# Define some test data:
x = numpy.array([0, 1, 2, 3, 4, 5, 6])
y = numpy.array([74.619623, 66.77367, 9.796839, 41.399514, 240.654016, 127.092583, 30.437209])
#x = numpy.linspace(0., numpy.pi)
#y = numpy.cos(x) + 0.05 * numpy.random.normal(size=len(x))

# p0 is the initial guess for the fitting coefficients, set the length
# of this to be the order of the polynomial you want to fit. Here I
# have set all the initial guesses to 1., you may have a better idea of
# what values to expect based on your data.
p0 = numpy.ones(6,)
print p0,x,y
coeff, var_matrix = curve_fit(_polynomial, x, y, p0=p0)

yfit = [_polynomial(xx, *tuple(coeff)) for xx in x] # I'm sure there is a better
                                                    # way of doing this

plt.plot(x, y, label='Test data')
plt.plot(x, yfit, label='fitted data')

plt.show()