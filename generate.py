import numpy as np

# generate uniform vals
prep_times = np.arange(0.05, 0.5001, 1/60)

assert len(prep_times) == 28

# we want 34 per block; repeat the upper few

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


# go_ means go by default block (use 'no' filler)
rng = np.random.RandomState(seed=1)
rng.shuffle(prep_times)
block1_switches = np.zeros((34, 3))
block1_switches[:, 0] = prep_times

go_block1 = block1_switches.copy()
go_block1[:, 1] = 1  # initial
go_block1[:, 2] = 0  # final

no_block1 = block1_switches.copy()
no_block1[:, 1] = 0  # initial
no_block1[:, 2] = 1  # final


# all 100 trials
go_block1 = np.vstack((go_block1, go_filler))
rng = np.random.RandomState(seed=2)
rng.shuffle(go_block1)
rng = np.random.RandomState(seed=2)
no_block1 = np.vstack((no_block1, no_filler))
rng.shuffle(no_block1)

# don't forget 5 softballs to start
go_block1 = np.vstack((go_easy, go_block1))
no_block1 = np.vstack((no_easy, no_block1))

np.savetxt('tables/go_default_block1.csv', go_block1, delimiter=',', header='t_prep,initial,final', comments='', fmt=['%10.5f', '%i', '%i'])
np.savetxt('tables/no_default_block1.csv', no_block1, delimiter=',', header='t_prep,initial,final', comments='', fmt=['%10.5f', '%i', '%i'])


# go_ means go by default block (use 'no' filler)
rng = np.random.RandomState(seed=2)
rng.shuffle(prep_times)
block2_switches = np.zeros((34, 3))
block2_switches[:, 0] = prep_times

go_block2 = block2_switches.copy()
go_block2[:, 1] = 1  # initial
go_block2[:, 2] = 0  # final

no_block2 = block2_switches.copy()
no_block2[:, 1] = 0  # initial
no_block2[:, 2] = 1  # final


# all 100 trials
go_block2 = np.vstack((go_block2, go_filler))
rng = np.random.RandomState(seed=3)
rng.shuffle(go_block2)
rng = np.random.RandomState(seed=3)
no_block2 = np.vstack((no_block2, no_filler))
rng.shuffle(no_block2)

# don't forget 5 softballs to start
go_block2 = np.vstack((go_easy, go_block2))
no_block2 = np.vstack((no_easy, no_block2))

np.savetxt('tables/go_default_block2.csv', go_block2, delimiter=',', header='t_prep,initial,final', comments='', fmt=['%10.5f', '%i', '%i'])
np.savetxt('tables/no_default_block2.csv', no_block2, delimiter=',', header='t_prep,initial,final', comments='', fmt=['%10.5f', '%i', '%i'])


# go_ means go by default block (use 'no' filler)
rng = np.random.RandomState(seed=3)
rng.shuffle(prep_times)
block3_switches = np.zeros((34, 3))
block3_switches[:, 0] = prep_times

go_block3 = block3_switches.copy()
go_block3[:, 1] = 1  # initial
go_block3[:, 2] = 0  # final

no_block3 = block3_switches.copy()
no_block3[:, 1] = 0  # initial
no_block3[:, 2] = 1  # final


# all 100 trials
go_block3 = np.vstack((go_block3, go_filler))
rng = np.random.RandomState(seed=4)
rng.shuffle(go_block3)
rng = np.random.RandomState(seed=4)
no_block3 = np.vstack((no_block3, no_filler))
rng.shuffle(no_block3)

# don't forget 5 softballs to start
go_block3 = np.vstack((go_easy, go_block3))
no_block3 = np.vstack((no_easy, no_block3))

np.savetxt('tables/go_default_block3.csv', go_block3, delimiter=',', header='t_prep,initial,final', comments='', fmt=['%10.5f', '%i', '%i'])
np.savetxt('tables/no_default_block3.csv', no_block3, delimiter=',', header='t_prep,initial,final', comments='', fmt=['%10.5f', '%i', '%i'])
