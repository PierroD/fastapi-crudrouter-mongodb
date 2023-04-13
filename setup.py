from setuptools import setup, find_packages



with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastapi-crudrouter-mongodb",
    version="0.0.4",
    author="Pierre DUVEAU",
    author_email="",
    description="A dynamic FastAPI router that automatically creates CRUD routes for your mongodb models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pierrod/fastapi-crudrouter-mongodb",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "pydantic",
        "pymongo",
        "motor"
    ],
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
)