from setuptools import setup, find_packages

setup(
    name="langchain-prompt-templates",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Зависимости, если нужны
    ],
    author="Your Name",
    description="Advanced prompt templates for LangChain with dynamic modification and conversion capabilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/langchain-prompt-templates",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)