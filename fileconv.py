#!/usr/bin/env python2
# -*- coding: utf-8 -*-

DIRECTORY = "Convtest"

import os      #, glob

for infile in os.listdir(DIRECTORY):
  number = ''
  for character in infile:
    if character.isdigit():
      number = character
  if number:
    print number




















  
#for infile in glob.glob(os.path.join(path, "*lek"+str(lesson_nr)+"*.doc")):