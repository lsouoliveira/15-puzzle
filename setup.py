from setuptools import setup

setup(
    name="15-puzzle",
    version="1.0.0",
    packages=["fifteen_puzzle", "fifteen_puzzle.gui"],
    package_dir={"fifteen_puzzle": "src"},
    package_data={"fifteen_puzzle.gui": ["data/**/*"]},
    author="Lucas Sousa",
    description="A 15 puzzle game made with pygame.",
    long_description=open("README.md").read(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX",
        "Programming Language :: Python",
    ],
    install_requires=["Pillow==9.4.0", "pygame==2.1.2"],
    python_requires=">=3.10.0",
    entry_points={
        "console_scripts": ["15-puzzle = fifteen_puzzle.__main__:main"],
    },
)
