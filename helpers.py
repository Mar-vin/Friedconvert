#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import codecs, os, cgi

#################### GLOBAL FUNCTIONS ##############

def message(text):
  print text

def create_directories(leclist):
  for lesson_nr in leclist:
    lekpath = "../lections/lek"+str(lesson_nr)+'/'
    os.system("mkdir " +lekpath)

def convert_to_html(lesson_list):
  ###Uses open office to convert all given doc-files to HTML
  message('converting raw docs to HTML')
  os.system('soffice -accept="socket,port=8100;urp;"')
  for lang in ["en", "sp"]:
    path = "../rawdocs/"+lang
    for lesson_nr in lesson_list:
      lekpath = "../lections/lek"+str(lesson_nr)+'/'
      for infile in glob.glob(os.path.join(path, "*lek-"+str(lesson_nr)+"-*.doc")):
        message('converting '+ infile)
        os.system('python DocumentConverter.py ' +infile +' ' +lekpath+'lek'+str(lesson_nr)+'_'+lang+'.html')

def isodd(number):
  if number%2 ==0:
    return False
  else:
    return True

def read_html(html_file):
  #Reads the content of the given file and returns it as a string.
  #Was at first only used for html-files.
  input_file = codecs.open(html_file, 'r', "utf-8")
  text = ""
  for line in input_file.readlines():
    text = text + line
  input_file.close()
  return text

def sanitize_snippet(snippet, onlytabs = False):
  #Clears a line of HTML of some annoying symbols.
  if not onlytabs:
    snippet = snippet.replace('\n',' ')
    snippet = snippet.replace('#','')
    snippet = snippet.strip()
  snippet = snippet.replace('\t','')
  return snippet

def htmlize(content):
  #translates the content from utf-8 to html
  return cgi.escape(content).encode('ascii', 'xmlcharrefreplace')