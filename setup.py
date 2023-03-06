'''
Setup for boardgametracker

from course material
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/flask-api-project-layout/
'''
from setuptools import find_packages, setup



setup(
    name="boardgametracker",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-caching",
        "flask-restful",
        "flask-sqlalchemy",
        "jsonschema",
        "SQLAlchemy"
    ]
    )
