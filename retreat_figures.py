# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 22:53:47 2013

@author: gonca_000
"""

storage_base = r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/'
talk_figures = storage_base + r'users/glopes/talks/retreat2013/figures'
#mclesions = [load_pickle(path) for path in [r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_20.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_21.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_22.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_23.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_24.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_25.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_26.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_27.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_28.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_29.pickle']]

################# Stacked Nose Trajectories ###############################

group_order = [0,2,4,6,8,1,3,5,7,9]
lesion_order = range(0,10,2)
sham_order = range(1,10,2)

## Split drawing example
#plot_trajectory_groups('all',t,lesion_order,[4],drawsteps=False,drawcolorbar=False)
#gcf().canvas.manager.window.setGeometry(640,345,640,706)

plt.close('all')
plot_trajectory_groups('all',t,group_order,[4],drawsteps=False)
gcf().canvas.manager.window.setGeometry(0,22,1366,706)

plt.close('all')
plot_trajectory_groups('all',t,group_order,[5],drawsteps=False)
gcf().canvas.manager.window.setGeometry(0,22,1366,706)

plt.close('all')
plot_trajectory_groups('all',t,group_order,[6],drawsteps=False)
gcf().canvas.manager.window.setGeometry(0,22,1366,706)

plt.close('all')
plot_trajectory_groups('all',t,group_order,[12],drawsteps=False)
gcf().canvas.manager.window.setGeometry(0,22,1366,706)

plt.close('all')
plot_trajectory_groups('all',t,[4,6,1,5],[16],drawsteps=False)
gcf().canvas.manager.window.setGeometry(0,22,1366,706)


############# Speed in Center vs Speed Outside ############################

def plot_speed_features_comparison(name,t,i):
    stable_features = np.concatenate([preprocess_speed_features(t.trajectories[i][j],t.slices[i][j],t.speeds[i][j])
                                      for j in [12]])
    stable_features = removerows(stable_features,np.logical_or(np.isnan(stable_features), stable_features > 50))

    def get_labeled_slices(slices,labels):
        return [slices[i] for i in get_labeled_indices(labels,{'state':'stable'})]
        #return slices

    manipulated_features = np.concatenate([preprocess_speed_features(t.trajectories[i][j],get_labeled_slices(t.slices[i][j],t.labels[i][j]),get_labeled_slices(t.speeds[i][j],t.labels[i][j]))
                                           for j in [14,15,16]])
    manipulated_features = removerows(manipulated_features,np.logical_or(np.isnan(manipulated_features), manipulated_features > 50))
    stable = plot_speed_features(name,stable_features,True,c='g',marker='o')
    manipulated = plot_speed_features(name,manipulated_features,True,c='r',marker='x')
    stable[0].gca().legend((stable[1],manipulated[1]),('state A','state A/B'),loc=4,scatterpoints=1)
    return stable[0]


plt.close('all')
plot_speed_features_comparison('jpak25',t,5)

tilefigures([plot_speed_features_comparison('jpak2%s' % i,t,i) for i in range(10)],[5,2])



#plt.close('all')
#stable = [plot_trajectory_speed_features('jpak25',t.trajectories[i][j],t.slices[i][j],t.speeds[i][j],
#                     c='g',marker='o')
#                     for i,j in zip([5,5,5],[3,4,12])]
#manipulated = [plot_trajectory_speed_features('jpak25',t.trajectories[i][j],t.slices[i][j],t.speeds[i][j],
#                     c='r',marker='x')
#                     for i,j in zip([5,5,5],[14,15,16])]
#xlim(0,25)
#ylim(0,25)
#gca().legend((stable[0][1], manipulated[0][1]), ('stable','manipulated'), loc=4,scatterpoints=1)

plt.close('all')
stable = [plot_trajectory_speed_features('jpak21',t.trajectories[i][j],t.slices[i][j],t.speeds[i][j],
                     c='g',marker='o')
                     for i,j in zip([1,1,1],[3,4,12])]
manipulated = [plot_trajectory_speed_features('jpak21',t.trajectories[i][j],t.slices[i][j],t.speeds[i][j],
                     c='r',marker='x')
                     for i,j in zip([1,1,1],[14,15,16])]
xlim(0,19)
ylim(0,19)
gca().legend((stable[0][1], manipulated[0][1]), ('stable','manipulated'), loc=4,scatterpoints=1)

plt.close('all')
stable = [plot_trajectory_speed_features('jpak22',t.trajectories[i][j],t.slices[i][j],t.speeds[i][j],
                     c='g',marker='o')
                     for i,j in zip([2,2,2],[3,4,12])]
manipulated = [plot_trajectory_speed_features('jpak22',t.trajectories[i][j],t.slices[i][j],t.speeds[i][j],
                     c='r',marker='x')
                     for i,j in zip([2,2,2],[14,15,16])]
xlim(0,15)
ylim(0,15)
gca().legend((stable[0][1], manipulated[0][1]), ('stable','manipulated'), loc=4,scatterpoints=1)

plt.close('all')
stable = [plot_trajectory_speed_features('jpak28',t.trajectories[i][j],t.slices[i][j],t.speeds[i][j],
                     c='g',marker='o')
                     for i,j in zip([8,8,8],[3,4,12])]
manipulated = [plot_trajectory_speed_features('jpak28',t.trajectories[i][j],t.slices[i][j],t.speeds[i][j],
                     c='r',marker='x')
                     for i,j in zip([8,8,8],[14,15,16])]
xlim(0,20)
ylim(0,20)
gca().legend((stable[0][1], manipulated[0][1]), ('stable','manipulated'), loc=4,scatterpoints=1)

############# Average Trial Times Across Sessions #########################
color_cycle = ['r' if i % 2 == 0 else 'b' for i in range(10)]
big_geometry = (640,345,960,532)

plt.close('all')
fig = plt.figure('mclesionshamA average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[plot_average_trial_times('mclesionshamA',mclesionsham[i][0:5],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(10)]
legend(('lesion','sham'))
save_figure(fig,talk_figures)

plt.close('all')
fig = plt.figure('mclesionshamB average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[plot_average_trial_times('mclesionshamB',mclesionsham[i][0:11],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(10)]
ylim(-110,800)
legend(('lesion','sham'))
save_figure(fig,talk_figures)

plt.close('all')
fig = plt.figure('mclesionshamC average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[plot_average_trial_times('mclesionshamC',mclesionsham[i][0:13],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(10)]
ylim(-110,800)
legend(('lesion','sham'))
save_figure(fig,talk_figures)

plt.close('all')
fig = plt.figure('mclesionshamD average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[plot_average_trial_times('mclesionshamD',mclesionsham[i][0:17],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(10)]
ylim(-110,800)
legend(('lesion','sham'))
fig.canvas.manager.window.setGeometry(big_geometry[0],big_geometry[1],big_geometry[2],big_geometry[3])
save_figure(fig,talk_figures)

plt.close('all')
fig = plt.figure('mclesionshamE average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[plot_average_trial_times('mclesionshamE',mclesionsham[i][0:23],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(10)]
ylim(-110,800)
legend(('lesion','sham'))
fig.canvas.manager.window.setGeometry(big_geometry[0],big_geometry[1],big_geometry[2],big_geometry[3])
save_figure(fig,talk_figures)

plt.close('all')
fig = plt.figure('mclesionshamF average tip height across sessions')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[plot_average_tip_height('mclesionshamF',mclesionsham[i][0:25],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(10)]
ylim(-110,800)
legend(('lesion','sham'))
fig.canvas.manager.window.setGeometry(big_geometry[0],big_geometry[1],big_geometry[2],big_geometry[3])
save_figure(fig,talk_figures)
###########################################################################