import numpy as np

# generate uniform vals
prep_times = np.arange(0.05, 0.5001, 1/60)

assert len(prep_times) == 28

# we want 34 per block; repeat the upper few to make it a little easier

extras = np.arange(0.4 + (1/60), 0.5001, 1/60)

assert len(extras) == 6

# paste together
prep_times = np.hstack((prep_times, extras))

# we want to write a table with [t_prep, initial, final]
# 6 go default, 6 no default


go_filler = np.full((100-34, 3), [0.5, 1, 1])
no_filler = np.full((100-34, 3), [0.5, 0, 0])

# default go, easy ones
go_easy = np.array([[0.5, 1, 1], [0.5, 1, 0], [0.5, 1, 1], [0.5, 1, 0], [0.5, 1, 1], [0.5, 1, 0]])
# default no, easy ones
no_easy = np.array([[0.5, 0, 0], [0.5, 0, 1], [0.5, 0, 0], [0.5, 0, 1], [0.5, 0, 0], [0.5, 0, 1]])

for i in range(6):
    rng = np.random.RandomState(seed=i)
    pt2 = prep_times.copy()
    rng.shuffle(pt2)
    block_switches = np.zeros((34, 3))
    block_switches[:, 0] = pt2
    go_block_stuff = block_switches.copy()
    go_block_stuff[:, 1] = 1
    go_block_stuff[:, 2] = 0
    no_block_stuff = block_switches.copy()
    no_block_stuff[:, 1] = 0  # initial
    no_block_stuff[:, 2] = 1  # final

    go_block_stuff = np.vstack((go_block_stuff, go_filler))
    rng = np.random.RandomState(seed=i+1)
    rng.shuffle(go_block_stuff)
    no_block_stuff = np.vstack((no_block_stuff, no_filler))
    rng = np.random.RandomState(seed=i+1)
    rng.shuffle(no_block_stuff)
    go_block_stuff = np.vstack((go_easy, go_block_stuff))
    no_block_stuff = np.vstack((no_easy, no_block_stuff))

    np.savetxt('tables/go_default_block%i.csv' % (i+1), go_block_stuff, delimiter=',',
               header='t_prep,initial,final', comments='', fmt=['%10.5f', '%i', '%i'])

    np.savetxt('tables/no_default_block%i.csv' % (i+1), no_block_stuff, delimiter=',',
               header='t_prep,initial,final', comments='', fmt=['%10.5f', '%i', '%i'])
