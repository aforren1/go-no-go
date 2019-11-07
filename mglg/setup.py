import setuptools
import sys

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="mglg",
    version="0.0.1",
    install_requires=requirements,
    author="Alex Forrence",
    author_email="adf@jhmi.edu",
    description="Desc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://none",
    packages=setuptools.find_packages(),
    package_data={'mglg': ['graphics/shader_src*']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
