import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")) as infile:
    long_description = infile.read()

setup(
    name="cllmv",
    version="0.1.2",
    description="Chutes fast LLM verification.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chutesai/cllmv",
    author="chutes.ai",
    license_expression="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "setuptools>=0.75",
    ],
    extras_require={
        "dev": [
            "ruff",
            "wheel",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
