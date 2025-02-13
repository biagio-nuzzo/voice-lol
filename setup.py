from setuptools import setup, find_packages

setup(
    name="fastchain",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["PyQt5", "vosk", "pyaudio"],
    entry_points={"console_scripts": ["fastchain=fastchain.cli:main"]},
)
