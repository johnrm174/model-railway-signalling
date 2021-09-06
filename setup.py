import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="model-railway-signals",
    version="2.1.0",
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
    packages=["model_railway_signals"],
    include_package_data=True,
    install_requires=["pyserial"]

)