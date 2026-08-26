from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="isbrokersafe",
    version="1.0.0",
    author="VasileDev Group",
    author_email="support@isbrokersafe.com",
    description="Official Python SDK for IsBrokerSafe Real-Time Financial Broker & Crypto Fraud Intelligence API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://isbrokersafe.com/api/v1/docs",
    project_urls={
        "Documentation": "https://isbrokersafe.com/api/v1/docs",
        "Source": "https://github.com/amendamax/isbrokersafe-python-sdk",
        "Tracker": "https://github.com/amendamax/isbrokersafe-python-sdk/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[],
    keywords="broker fraud forex crypto scam detection finance security compliance fca cysec whois",
)
