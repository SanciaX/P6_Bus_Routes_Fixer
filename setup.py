
from setuptools import setup, find_packages
import os

# Read README.md and requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='bus_routes_fixer',
    version='1.0',
    author="Shanshan Xie",
    author_email="shanshanxie@tfl.gov.uk",
    description="TfL P6 ONE Model Bus Routes Fixer",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/SanciaX/P6_Bus_Routes_Fixer",
    project_urls={"Bug Tracker": "https://github.com/SanciaX/P6_Bus_Routes_Fixer/issues"},
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.9',
)
