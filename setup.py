import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    "aiohttp==3.8.6"
]

setuptools.setup(
    name="simulator",
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
        "console_scripts": ["simulator = simulator.entrypoint:run"]},
)