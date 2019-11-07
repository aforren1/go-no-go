import setuptools
import sys
import re

VERSIONFILE = "gonogo/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

with open("readme.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="gonogo",
    version=verstr,
    install_requires=requirements,
    author="Alex Forrence",
    author_email="adf@jhmi.edu",
    description="Desc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aforren1/go-no-go",
    packages=setuptools.find_packages(),
    package_data={'gonogo': ['resources/*']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
