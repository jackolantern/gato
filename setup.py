import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gato",
    version="0.0.1",
    author="John Connor",
    author_email="john.theman.connor@gmail.com",
    description="A utility to display images in a KiTTY terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jackolantern/gato",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GPLv3",
        "Operating System :: Linux",
    ],
)
