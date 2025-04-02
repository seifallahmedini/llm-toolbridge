from setuptools import setup, find_packages

setup(
    name="llm_toolbridge",
    version="0.1.0",
    description="A unified tool calling interface for LLM providers",
    author="LLM Tool Bridge Team",
    author_email="example@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) <= 1:
        print("Error: No arguments provided.")
        print("Please use `pip install .` or `pip install -e .` to install this package")
        sys.exit(1)
    # If we have arguments, let setuptools handle them normally