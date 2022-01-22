import pathlib
from setuptools import setup
from setuptools import find_packages

print (find_packages())

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="model-railway-signals",
    version="2.6.2",
    packages=find_packages(),
    include_package_data=True,
    description="Create your own DCC model railway signalling scheme",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/johnrm174/model-railway-signalling",
    author="johnrm174",
    author_email="johnrm17418@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=["pyserial","paho-mqtt"]

)