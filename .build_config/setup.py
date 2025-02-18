from setuptools import setup, find_packages

setup(
    name="cryptoblade",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=43.0.1",
        "prompt_toolkit>=3.0.48",
        "rich>=13.9.1",
        "tqdm>=4.66.5",
        "numpy>=2.1.1",
        "pytest>=8.3.4",
        "coverage>=7.6.10",
        "pytest-cov>=6.0.0",
    ],
)
