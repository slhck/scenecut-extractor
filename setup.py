# Always prefer setuptools over distutils
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# Versioning
with open(os.path.join(here, "scenecut_extractor", "__init__.py")) as version_file:
    for line in version_file:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"')
            break

# Get the long description from the README file
with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

setup(
    name="scenecut_extractor",
    version=version,
    description="Get scenecuts from a video file using ffmpeg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slhck/scenecut-extractor",
    author="Werner Robitza",
    author_email="werner.robitza@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=["tqdm>=4.38.0", "ffmpeg-progress-yield"],
    packages=["scenecut_extractor"],
    include_package_data=True,
    package_data={
        "scenecut_extractor": ["py.typed"],
    },
    entry_points={
        "console_scripts": [
            "scenecut-extractor=scenecut_extractor.__main__:main",
        ],
    },
)
