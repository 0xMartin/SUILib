from setuptools import setup, find_packages

setup(
    name="SUILib",
    version="0.1.0",
    description="Simple UI Library for Pygame applications",
    author="Martin Krcma",
    author_email="martin.krcma1@gmail.com",
    url="https://github.com/0xMartin/SUILib",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pygame",
        "matplotlib",
        "numpy"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)