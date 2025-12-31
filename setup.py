"""
setup.py - Visiontegral Packaging Script
Author: Visionis
"""
from setuptools import setup, find_packages

setup(
    name="visiontegral",
    version="1.0.0",
    author="Visionis",
    description="A Cinematic & High-Performance Multidimensional Integration Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Visionis/Visiontegral", # Temsili URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "plotly>=5.3.0",
        "manim>=0.13.0",
    ],
    python_requires=">=3.8",
)

