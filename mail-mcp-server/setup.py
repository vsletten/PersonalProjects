from setuptools import setup, find_packages

setup(
    name="mcp-graph-server",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==2.3.2",
        "Flask-Session==0.5.0",
        "python-dotenv==1.0.0",
        "msal==1.22.0",
        "requests==2.30.0",
        "Werkzeug==2.3.4",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="MCP Server for Microsoft Graph API messages endpoint",
    keywords="MCP, Graph API, Microsoft, email",
    url="https://github.com/yourusername/mcp-graph-server",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
)
