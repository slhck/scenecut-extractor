# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))

# Versioning
with open(os.path.join(here, 'scenecut_extractor', '__init__.py')) as version_file:
    version = eval(version_file.read().split("\n")[0].split("=")[1].strip())

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

try:
    import pypandoc
    long_description = pypandoc.convert_text(long_description, 'rst', format='md')
except ImportError:
    print("pypandoc module not found, could not convert Markdown to RST")

setup(
    name='scenecut_extractor',
    version=version,
    description='Get scenecuts from a video file using ffmpeg',
    long_description=long_description,
    url='https://github.com/slhck/scenecut-extractor',
    author='Werner Robitza',
    author_email='werner.robitza@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Video',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['scenecut_extractor'],
    entry_points={
        'console_scripts': [
            'scenecut_extractor=scenecut_extractor.__main__:main',
        ],
    },
)
