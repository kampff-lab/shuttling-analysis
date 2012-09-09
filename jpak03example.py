# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 14:53:59 2012

@author: IntelligentSystems
"""

plt.close('all')
plot_session(jpak03control)
plot_session(jpak03manip1)
plot_session(jpak03manip2)

plot_speed_raster('jpak03',jpak03control.tip_horizontal_path + jpak03manip1.tip_horizontal_path + jpak03manip2.tip_horizontal_path)
