# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import os

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)