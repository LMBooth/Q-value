# Extended Q-Value: Experiment Software

The following repository hosts custom made Python code which was developed for the purpose of experimental testing for time taken to answer a question vs a rated Q-value.

The experimental procedure entails 48 questions between Q-values of 0.6-6.99, each question set is randomised but has 3 questions from each of the 16 Q-value buckets separated by a space of 0.4.
i.e. 2 questions from 0.6-0.99 Q-value, 2 questions from 1.00-1.39... 2 questions from 6.60-6.99.

## Install Python Dependencies 

```bash

# Use the Python 3 installation of your choice. - (Remember kivy does not install on Python 3.8+ yet, as of 06/07/2020)
# Windows Installation Example
python -m pip install matplotlib lmfit xlsxwriter scipy

# The GUI software is written in Kivy language, as such the kivy libraries must be installed
# Update tools for installing kivy
python -m pip install --upgrade pip wheel setuptools virtualenv

# Install kivy dependencies
python -m pip install docutils pygments pypiwin32 kivy_deps.sdl2==0.1.* kivy_deps.glew==0.1.*
python -m pip install kivy_deps.gstreamer==0.1.*

# if Python 3.5+ (kivy is not yet compatible with Python 3.8+ so only earlier versions are compatible)
python -m pip install kivy_deps.angle==0.1.*

# Install kivy:
python -m pip install kivy==1.11.1

# Follow kivy windows installatin guide for more info: 
# https://kivy.org/doc/stable/installation/installation-windows.html

```
