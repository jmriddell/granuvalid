from setuptools import setup, find_packages

setup(
    name="validpeas",
    version="0.1",
    packages=find_packages(),
    description="Tools for structured validations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Juan Ezequiel Molina Riddell",
    author_email="jmriddell@protonmain.ch",
    url="https://github.com/jmriddell/validpeas",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="validation",
    install_requires=["pydantic"],
    package_data={"validpeas": ["py.typed"]},
)
