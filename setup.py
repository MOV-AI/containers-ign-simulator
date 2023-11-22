""" Setup file for the simulator_api package. """

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    "flask==2.2.5",
    "requests==2.22.0",
    "werkzeug==2.0",
    "webservercore==1.1.0.4",
    "celery==5.3.5",
    "SQLAlchemy==2.0.23",
]

setuptools.setup(
    name="simulator_api",
    version="3.0.0-1",
    author="Devops team",
    author_email="devops@mov.ai",
    description="Simulator web service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MOV-AI/containers-ign-simulator",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={'': ['config.ini']},
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=requirements,
)
