from setuptools import setup, find_packages

setup(
    name="gateway_service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-jose[cryptography]",
        "python-multipart",
        "requests",
        "pika",
        "python-dotenv"
    ],
) 