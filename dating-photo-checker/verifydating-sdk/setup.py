from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="verifydating",
    version="1.0.0",
    author="VasileDev Group",
    author_email="support@verifydating.net",
    description="Official Python SDK for VerifyDating Real-Time Facial Scam Intelligence & Anti-Catfish API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://verifydating.net/api/v1/dating-docs",
    project_urls={
        "Documentation": "https://verifydating.net/api/v1/dating-docs",
        "Source": "https://github.com/amendamax/verifydating-python-sdk",
        "Tracker": "https://github.com/amendamax/verifydating-python-sdk/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
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
    keywords="dating catfish romance scam detection facial recognition deepfake defense trust safety identity moderation",
)
