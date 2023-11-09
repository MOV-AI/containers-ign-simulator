import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    "flask==2.1.2", 
    "requests", 
    "werkzeug==2.0", 
    "webservercore==1.1.0.1",
    "celery"
]

setuptools.setup(
    name="simulator_api",
    version="0.0.1-1",
    author="Devops team",
    author_email="devops@mov.ai",
    description="Simulator web service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MOV-AI/containers-ign-simulator",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=requirements,
    entry_points={
        "console_scripts": ["simulator_api = simulator_api.entrypoint:run"]},
)