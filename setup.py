import pathlib
from setuptools import setup
from setuptools import find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="model-railway-signals",
    version="3.3.0",
    packages=find_packages(),
    include_package_data=True,
    description="Create your own DCC model railway signalling scheme",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/johnrm174/model-railway-signalling",
    author="johnrm174",
    author_email="johnrm17418@gmail.com",
    license="GNU GENERAL PUBLIC LICENSE Version 2, June 1991",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=["pyserial","paho-mqtt"]

)