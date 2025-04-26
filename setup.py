from setuptools import setup, find_packages

setup(
    name="schedulur",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.4.2",
        "google-api-python-client>=2.90.0",
        "google-auth-httplib2>=0.1.0",
        "google-auth-oauthlib>=1.0.0",
        "python-dateutil>=2.8.2",
        "twilio>=8.2.2",
    ],
    entry_points={
        "console_scripts": [
            "schedulur=schedulur.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Schedulur Team",
    author_email="team@schedulur.com",
    description="A personal medical appointment scheduling system",
    keywords="scheduling, appointments, healthcare",
    url="https://github.com/schedulur/schedulur",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)