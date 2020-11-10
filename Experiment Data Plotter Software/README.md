# Extended Q-Value: Experiment Data Plotter Software

The following repository hosts the saved, annonimised participant data and custom data viewer for the experimental software provided [here](https://github.com/LMBooth/Q-value/tree/master/Experiment%20Software ).

## Recorded SQL Database Structure 
The file 'participantmerged.db' contains all the results from a 13-particpant group of all male 19-30 3rd year or Masters Engineering students taking part in the provided software. The SQL Database has columns; idnum, digit1, digit2, answer, actualanswer, q, time and rating.

- Id =  The order which the question was asked to the participant.
- Digit1 =  the left number presented.
- Digit2 =  The right number presented.
- Answer =  Answer given by the participant for adding digit1 and digit2.
- Actual answer =  Actual answer for digit1 + digit2.
- Q-Value =  The given Q-value for digit1 + digit2.
- Time = The time taken to answer digit1 + digit2.
- Rating = Subjective rating given by participant after each question, taken from a slider giving values between 0-100, where 0 is Very easy and 100 is Very hard.

From the above variables, the plotter software calculates three more variables: normrating, fixedq, elements and modified elements.

- Normalised rating = This variable is used to normalise all subjective ratings by the participants between a scale of 0 and a 100, as some participants have a tendency to rate every either easier or harder.
- Modified Q-value = This Q-value takes in to account the scaled factor for c every times a carry over occurs. i.e. 1 carry is c=1, 2 carries becomes c=(1+10), 3 carries becomes c=(1+10+100) and so on.
- Elements = Elements disregards the digit size and only adds 1 if a carry over occurs or for every digit that is interacting. This is done to think of each carry over or digit as a 'chunk' of required memory.
- Modified elements = Similar to elements, though the scaled factor applied to c in modifiedq is also used to account for the increasing cognitive demand from each carry-over.

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
