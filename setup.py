"""
Weather Flight Analyzer Package Setup

This script configures the package for distribution and installation.
It reads package metadata from README.md and dependencies from requirements.txt.

Authors: George Nassef, Will Landau
Copyright © 2021
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read package description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read package dependencies from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() 
        for line in fh 
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="weather-flight-analyzer",
    version="0.1.0",
    # Package metadata
    author="George Nassef, Will Landau",
    author_email="",  # Email addresses removed for privacy
    license="MIT",
    platforms=["any"],
    description="A tool for analyzing weather and flight data for delay prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/george-nassef/weather-flight-analyzer",
    packages=find_packages(),
    # Package classification
    classifiers=[
        # Development status
        "Development Status :: 3 - Alpha",
        
        # Intended audience
        "Intended Audience :: Aviation Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Python versions
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        
        # Environment and topics
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    # Package requirements
    python_requires=">=3.11",
    install_requires=requirements,
    
    # Command-line entry points
    entry_points={
        "console_scripts": [
            "weather-flight-analyzer=weather_flight_analyzer.__main__:main",
        ],
    },
    
    # Package data
    include_package_data=True,
    zip_safe=False,
)
