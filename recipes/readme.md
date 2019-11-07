These recipe files define the order of experiments and trial-by-trial settings.

A few rules and notes:

1. The recipe files must always end with the `.toml` extension (so the executable finds them)
2. The recipe files must be located in the `recipes/` directory, which should be immediately adjacent to the `drop.exe` file.
  - Recipe files *can* be located in folders within the `recipes/` directory, e.g. you could have a `recipes/march/session.toml` recipe.
  - To see which settings are allowed per experiment, see the `recipes/defaults` folder. For best results, do not modify the files in that folder.

[TOML](https://en.wikipedia.org/wiki/TOML) (Tom's Obvious, Minimal Language) is a fairly popular, easy-to-read, plain-text configuration file format. I believe it has sufficient flexibility to fully describe all the situations we may encounter when specifying experiments, and happens to have a parser that is distributed with all recent Python distributions. Within this language, we do expect a particular format for specifying sessions.

For example, below is one such TOML file:

```
[1]
name = 'practice'
consecutive = 5
# y_ball = 0.2 # octothorpes can be used for comments

[2]
name = 'arc'
angle_ref = {fun = 'choice', kwargs = {options=[80, 100], probs=[0.5, 0.5], seed=1}}

[3]
name = 'tap'

[4]
name = 'arc'
file = 'foo.csv' # contains columns with headers "t_prep", "angle_offset"
trials = 3

```

General notes:
  - Minimally, each block must have a key (e.g. `[a]`, `[1]`) and a name (e.g. `practice`, `arc`, `left_right`)
  - Keys must be unique.
  - The value of the key is used to uniquely identify repeats of a block type
  - The names are used to decide which task type is used. There are ~6 currently implemented (see notes for which ones)
  - Specifying keys beyond the name overrides the default value for that setting
  - Nearly any setting (except `trials`, `file`, `name`) can vary using one of the below functions.
  - If using one of the below functions, set the `seed` to get repeatable results.


Notes for `[a]`:
  - This is a practice block
  - Rather than using the default 4 consecutive trials to advance, we bumped it up to 5
  - Otherwise, the settings from `recipes/defaults/practice.toml` are used (e.g. `y_ball = 0.4`, `y_line = 0.3`, ...)

Notes for `[1]`:
  - This is the arc task
  - The reference angle of the arc changes trial by trial, determined by the `choice` function. It chooses between 80 and 100 degrees w/ equal probability, and a fixed seed of 1 (so we get the same result out each time)
  - Only specific functions are allowed, and must follow special rules for inclusion. More below.

Notes for `[0]`:
  - This is the tapping task, with no settings overridden.

Notes for `[x]`:
  - This is the arc task again
  - Rather than setting the `t_prep` and `angle_offset` directly in this file, we read them from a pre-specified csv file. ONLY csv files are currently allowed.
  - The `trials` setting is ineffectual-- when a file is specified, the number of rows in the file has full control over the number of trials

After block `[x]`, the session will end.

# Current Task Types

The following tasks are currently implemented under this new system:

 - 'practice': Practice timing until criterion met (n consecutive trials w/ good timing)
 - 'left_right': Press left key if ball on left, right key if ball on right of center line
 - 'go_no': Press key when ball is white, no press when ball is black
 - 'arc': Press left key if ball will land to the left of the center point on the arc, press the right key if the ball will land on the right
 - 'tap': Synchronize tapping of left key with the ball bouncing between two walls. Ball may disapper, but continue to keep timing until feedback appears.
 - 'timing': Ball may disappear while moving. Try to time left key press with when the ball would've intersected with the line.

'jump' (from previous implementation) is still pending. 

# Current Blessed Functions

The current "blessed" functions (i.e. if you feed the name into a TOML file with the right arguments, the expected things happen) are:

 - "uniform": kwargs = low, high, seed
   - lower bound and upper bound of uniform distribution
 - "normal": kwargs = loc, scale, seed
   - Location and scale of normal/gaussian distribution
 - "choice": kwargs = options, probs, seed
   - options: list of options (e.g. [0.3, 0.4]),
   - probs: Matching length list of probs (e.g. [0.6, 0.4]), must sum to 1
 - "criterion": kwargs = values, consecutive
   - values: list of values [0.5, 0.4, 0.3]
   - consecutive: particular number of 'correct_choices' that must occur sequentially to meet criterion

Some kwargs do have default values, but it would be better not to rely on them.

# Files

The blessed functions currently only generate values for a single setting at a time, so it's difficult to have settings that are not independent (e.g. if you wanted setting A to be lower when setting B == 3). Files can let you achieve those sorts of things, because they are externally generated and aren't limited to independence. They can be generated in anything that can produce a CSV, in principle (MATLAB, Excel, ...). 

I haven't yet devised *where* these files should live. For accessibility, it'll be in the root directory, i.e.:

```
drop.exe
recipes/
tables/ <- here
```

# Future

 - Auto-generate a reasonable `recipes/` directory if missing
 - Auto-generate a `tables/` directory if missing

I've figured out a syntax that would be good for specifying functions that set multiple settings. It'll look something like:

```
[3]
name = 'go_no'
multi = [{fun = 'gn_f', out = ['t_prep', 'initial', 'final'], kwargs={seed=1}},
         {fun = 'fun2', out = ['y_line', 'y_ball'], kwargs = {seed=1, min_dist=0.4}}]
```

Where `gn_f`, `fun2` are made-up functions that return multiple values. Those values will be assigned to the settings specified in `out`. This could effectively replace `file` in appropriate situations, although the function would still need to be baked into the executable. Things to resolve:

 - Conflicts with `file`, other `multi` functions (e.g. if both have a matching `out` key)
 - What the actual storage/calling in python looks like. Unclear-- do we keep a separate list of `multi`, and iterate through separately after the other settings have had a go?

This is somewhat lower on the priority list, because `file` is more flexible and doesn't require re-baking of the exe.
