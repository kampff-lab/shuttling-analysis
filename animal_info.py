# -*- coding: utf-8 -*-
"""
Created on Sun Nov 03 15:10:24 2013

@author: gonca_000
"""

import dateutil
import numpy as np

database = [np.genfromtxt(path,dtype=str,delimiter=',') for path in
[r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_20.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_21.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_22.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_23.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_24.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_25.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_26.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_27.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_28.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_29.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_36.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_37.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_38.csv',
r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/animals/JPAK_39.csv']]

birth = [(dateutil.parser.parse(animal[0,0]),animal[0,2]) for animal in database]
surgeries = [np.nonzero([x[1].startswith('Surgery') for x in animal])[0][slice(1)] for animal in database]
surgeries = [[dateutil.parser.parse(database[a][i,0]) for i in s] for a,s in enumerate(surgeries)]
surgery_age = [(s[0]-b[0]).days for b,s in zip(birth,surgeries) if len(s) > 0]
handling = [dateutil.parser.parse(animal[np.nonzero([x[1].startswith('Handling') for x in animal])[0][0],0]) for animal in database]
behavior = [dateutil.parser.parse(animal[np.nonzero([x[1].startswith('Behavior') for x in animal])[0][0],0]) for animal in database]
isolation_recovery_period = [(h-s[0]).days for s,h in zip(surgeries,handling) if len(s) > 0]
full_recovery_period = [(b-s[0]).days for s,b in zip(surgeries,behavior) if len(s) > 0]