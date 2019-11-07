
Data format:

data/subject_id/datetime/experiment_type/block[n]/[block data]

Within the `datetime` level, there are three files:
 - Copy of the recipe file used (.toml)
 - Json copy of the recipe file (.json)
 - settings file, containing:
   - recipe hash (to easily compare if same recipe; look at locality-sensitive hashing?)
   - operating system (from `platform.platform()`)
   - Python version (e.g. `3.7.4`)
   - Rush allowed? true/false
   - Frames per second (e.g. 60, 144, ...) from ExpWindow
   - GPU used (`GL_RENDERER`)
   - Response device used

Not sure:
 - Environment file w/ python package versions (`conda list` from env used to package exe)

The [n] at the block level is the key used for that block in the recipe

The [n] key should also be recorded as a block-level setting for easy access if neeed,
rather than having users parse apart some aspect of the data path
(We already have a `block_settings.json` that we can put it in)

## Building

Make a source archive w/o extra files via `git archive -o gonogo.zip HEAD && git submodule --quiet foreach 'cd $toplevel; zip -ru gonogo.zip $path'`.

1. Make a new virtual environment/conda environment with python 3.7+ and activate it.
    - If using conda, avoid using the conda version of numpy (which carries the MKL along with it)
2. Extract the source of `gonogo` to somewhere sensible
3. Change the working directory to that one
4. Run `bash ./preinstaller.sh` (linux) or `preinstaller.bat` (windows)
5. Install `gonogo` (`pip install .`, if you're in the `gonogo` directory)
6. Generate the exe with:

(semicolons & double quotes on windoze, colons on linux)
Linux:
`pyinstaller --noconsole --onefile --add-data 'gonogo/resources/fonts/*.ttf:gonogo/resources/fonts/' --add-data 'gonogo/resources/images/*.png:gonogo/resources/images/' --add-data 'gonogo/resources/sound/*.wav:gonogo/resources/sound/' drop.py`

Windows:
`pyinstaller --noconsole --onefile --add-data "gonogo/resources/fonts/*.ttf;gonogo/resources/fonts/" --add-data "gonogo/resources/images/*.png;gonogo/resources/images/" --add-data "dlls/freetype.dll;." drop.py`

(no cross-compilation allowed, AFAIK)

7. Then copy recipes in with

`cp -r recipes/ dist/`

(TODO: should generate reasonable defaults if no recipes folder)

8. Can zip up the `dist/` folder and send elsewhere.

## Other notes

find (potential) dropped frames:
First, `shopt -s globstar`

```
for d in **/*dropped*/drop*.json; do ls -l $d | awk '{if ($5 > 2) print $9}'; done
```

Gives me:

```
(py373) adf@adf-UX360CA:~/Documents/chris$ for d in **/*dropped*/drop*.json; do ls -l $d | awk '{if ($5 > 2) print $9}'; done
002/blocks_190910_130229/go_no/block21/dropped_frames/dropped_frames_trial25.json
Alkis/blocks_190910_145105/practice/blockp1/dropped_frames/dropped_frames_trial0.json
tim/blocks_190906_101116/go_no/block8/dropped_frames/dropped_frames_trial4.json

```
