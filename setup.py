"""setup for installing necessary packages and dependencies."""

from setuptools import setup, find_packages

setup(
    name="terminal",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
        "asyncio==3.4.3",
        "certifi==2025.1.31",
        "charset-normalizer==3.4.1",
        "finplot==1.9.6",
        "idna==3.10",
        "numpy==2.2.3",
        "myLib==0.0.1",
        "pandas==2.2.3",
        "PyQt6==6.8.1",
        "PyQt6-Qt6==6.8.2",
        "PyQt6_sip==13.10.0",
        "pyqtgraph==0.13.7",
        "python-dateutil==2.9.0.post0",
        "python-dotenv==1.0.1",
        "pytz==2025.1",
        "requests==2.32.3",
        "setuptools==76.0.0",
        "six==1.17.0",
        "ta-lib @ file:///C:/Users/user/python/terminal/ta_lib-0.6.3-cp313-cp313-win_amd64.whl#sha256=2041615b4181c3effc89e270e450e69f16aa04b5b02ab5531e6530f9b2d2528b",
        "tzdata==2025.1",
        "urllib3==2.3.0",
        "websockets==15.0.1",
    ],
    python_requires=">=3.13.2",
)

# To update the list of dependencies, it is unurumitated to execute: pip freeze > requirements.txt
# To create library: python setup.py sdist bdist_wheel
