from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="QuantResearch",
    version="0.0.2",
    author="Vinayak Shinde" "Vishal Mishra",
    author_email="vinayak.r.shinde.1729@gmail.com",
    description="Technical indicators and visualization tools for quantitative research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vinayak1729-web/QuantR",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "yfinance>=0.2.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
    ],)