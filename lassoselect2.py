import numpy as np

from matplotlib.widgets import LassoSelector
from matplotlib.path import Path

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    plt.ion()
    data = np.random.rand(100, 2)

    subplot_kw = dict(xlim=(0, 1), ylim=(0, 1), autoscale_on=False)
    fig, ax = plt.subplots(subplot_kw=subplot_kw)

    pts = ax.plot(data[:, 0], data[:, 1],'.')
    
    def onselect(verts):
        print verts
    
    lasso = LassoSelector(ax,onselect)
    #selector = SelectFromCollection(ax, pts)