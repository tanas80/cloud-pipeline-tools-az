from setuptools import find_packages, setup

setup(
    name="azurebatch-cleanup",
    version="0.1.0",
    description="Cleanup Azure Batch jobs not in completed state",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.0",
        "pydantic>=2.0",
        "tqdm>=4.60",
        "python-dotenv>=1.0",
        "pytimeparse>=1.1",
    ],
    extras_require={"dev": ["pytest>=7.0"]},
    entry_points={
        "console_scripts": [
            "azbatch-cleanup=azurebatch_cleanup.cli:main",
        ]
    },
)
