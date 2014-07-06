"""
Show how to use a lasso to select a set of points and get the indices
of the selected points.  A callback is used to change the color of the
selected points

This is currently a proof-of-concept implementation (though it is
usable as is).  There will be some refinement of the API.
"""
from matplotlib import path
from matplotlib.widgets import Lasso
import matplotlib.pyplot as plt
import numpy as np

class LassoManager(object):
    def __init__(self, ax, data, onselect=None):
        self.axes = ax
        self.canvas = ax.figure.canvas
        self.artist = None
        self.setdata(data)

        self.Nxy = len(data)
        self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)
        self.highlight = None
        self.onselect = onselect
        
    def setdata(self,data):
        self.data = data
        if self.artist:
            self.artist.remove()
        self.artist = self.axes.plot(self.data[:,0],self.data[:,1],'b.')[0]

    def callback(self, verts):
        try:
            p = path.Path(verts)
            ind = p.contains_points(self.data)
            self.highlight = self.axes.plot(self.data[ind,0],self.data[ind,1],'r.')[0]
            self.canvas.draw_idle()
            if self.onselect:
                self.onselect(self.data,ind)
        finally:
            self.canvas.widgetlock.release(self.lasso)
            del self.lasso

    def onpress(self, event):
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        if self.highlight:
            self.highlight.remove()
            self.highlight=None
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)

if __name__ == '__main__':

    data = np.random.rand(100, 2)

    ax = plt.subplot(111)
    ax.plot(data[:,0],data[:,1],'.')
    lman = LassoManager(ax, data)

    plt.show()