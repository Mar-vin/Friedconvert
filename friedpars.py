#!/usr/bin/env python2
# -*- coding: utf-8 -*-

################### CONFIG ############################

#PATH = "../lections/lek"+str(lesson_nr)+"/"

#OUTFILE = PATH+"lek"+str(lesson_nr)+"_LL.html"
#SRCFILE = PATH+"lek"+str(lesson_nr)+".html"
#XMLFILE = PATH+"lek"+str(lesson_nr)+".xml"

#HTML Templates and Colorcodes to use in the write_html function
HTMLRES_Path = "HTMLRES"

colordic = {"Header":"#000066", "Text": "#0099cc"}
colordic["Wortschatz"] = "#99ffcc"
colordic["Grammatik"] ="#ff6699"
colordic[u'\xdcbungen'] = "#0099cc"
colordic[u'Fragen'] = "#0099cc"
colordic[u'Aufgaben'] = "#0099cc"

merkdic = {"Header":"merkzeichen-l.jpg", "Text": "merkzeichen-t.jpg"}
merkdic["Wortschatz"] = "merkzeichen-w.jpg"
merkdic["Grammatik"] ="merkzeichen-g.jpg"
merkdic[u'\xdcbungen'] = "merkzeichen-t.jpg"
merkdic[u'Fragen'] = "merkzeichen-t.jpg"
merkdic[u'Aufgaben'] = "merkzeichen-t.jpg"

###############################################################

import codecs, os, glob, cgi
from HTMLParser import HTMLParser

global label_nr

label_nr = 1

################## PARSER ##############################

class MyHTMLParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.snipdic = {"captionlist" : []}
    self.snipdic["snipsecdict"] = {}
    self.snipdic["sniplist"] = []
    self.section = 'Header'
    self.snipdic["snipsecdict"]['Header']=''
    self.snipdic["sniptext"] = ''
    self.active = False
    self.inlist = []

  def handle_data(self, text):
    snipsecdict = self.snipdic["snipsecdict"]
    tagtext = repr(self.get_starttag_text())
    if tagtext.count("BODY") == 1:
      self.active = True
      
    if self.active:
      snippet = unicode(text)
      self.snipdic["sniptext"] += snippet

      for i in range(1,7):
        if sanitize_snippet(text, False) !=  '':
          if tagtext.count("H"+str(i)) == 1 :
            caption = sanitize_snippet(text, False)
            self.section = sanitize_snippet(snippet, False)
            self.snipdic["captionlist"].append(caption)
            snipsecdict[self.section] = ''
            return

      snipsecdict[self.section] = snipsecdict[self.section] + snippet
      self.snipdic["sniplist"].append(snippet)
##################### //PARSER #######################

##################### DEHASHER #######################

class Dehasher(object):
  def __init__(self, lesson_nr):
    self.inlist = []
    self.lesson_nr = lesson_nr

  def dehash(self, string):
    outsnips = []
    insnips = []
    i = 0
    for snippet in string.split("#"):
      sanitize_snippet(snippet, False) ##### Hier snippet = san... ???
      if snippet != '':
        if isodd(i):
          insnips.append(snippet)
        else:
          outsnips.append(snippet)
      i+=1
    return {"outsnips": outsnips, "insnips":insnips}

  def rebuild(self, dehashed_dict, section):
    ##rebuilds a string from an outsnips-insnips dictionary, replacing the insnips with
    ##a Label.
    global label_nr
    ins = dehashed_dict["insnips"]
    self.inlist.extend(ins)
    outs = dehashed_dict["outsnips"]
    new_text = ''
    i=1
    for snip in outs:
      new_text = new_text + snip
      if len(ins) != 0 and i != len(outs):
        new_text = new_text + "###_LL_LABEL_LESSON"+str(self.lesson_nr)+"_ITEM"+str(label_nr)+"###"
        i+=1
        label_nr +=1
    return new_text

#################### //DEHASHER ####################

#################### WRITER ########################

class Writer(object):
  def __init__(self, dehasher, PATH):
    self.output = ''
    self.dehasher = dehasher
    self.lesson_nr = dehasher.lesson_nr
    self.PATH = PATH

  def create_header(self, lektitle):
  #Write the Header
    #Read the lines of the different templates
    for vorlage in ["Head.txt"]:
      vorfile = codecs.open(HTMLRES_Path + "/"+vorlage, 'r', "utf-8")
      lines = vorfile.readlines()
      vorfile.close()
      #And write them in the new file, replacing ###TEXT### with the content
    for line in lines:
      line = line.replace("###COLOR###", colordic["Header"])
      line = line.replace("###LEKNR###", 'Lektion '+str(self.lesson_nr))
      line = line.replace("###LEKTITLE###", htmlize(lektitle))
      self.output += line
      #outfile.write(line)

  def create_html(self, snipdic):
    #TODO: Hier noch die snipseclist benutzen für die
    #automatische Erstellung von verschiedenen Abschnitten

    snipsecdict = snipdic["snipsecdict"]
    captionlist = snipdic["captionlist"]
    try:
      lektitle = captionlist[0]
    except IndexError:
      message("Problem with finding captions. Probably no Hx-tags in the file.")
      return
    captionlist = captionlist[1:len(captionlist)]
    self.create_header(lektitle)
    self.create_content(captionlist, snipsecdict)
    self.create_footer

  def create_content(self, captionlist, snipsecdict):
    #write the content
    for section in captionlist:
      if section == u"Übungen":
        pass
      else:
        #if osPATH+"lek"+str(lesson_nr)+"_"+section+".txt":
        content = snipsecdict[section]
        dehashed_dict = self.dehasher.dehash(content)
        content = self.dehasher.rebuild(dehashed_dict, section)
        content = htmlize(content)
        try:
          san_section= section.replace('/','')
          f = open(self.PATH+"lek"+str(self.lesson_nr)+"_"+san_section+".txt")
          content = f.read()
        except IOError:
          self.write_sec_txt(content, section)
        self.create_sec_title(section)
        self.create_body(content, section)

  def create_sec_title(self, section):
    for vorlage in ["SectionTitle.txt"]:
      vorfile = codecs.open(HTMLRES_Path + "/"+vorlage, 'r', "utf-8")
      lines = vorfile.readlines()
      vorfile.close()
        #And write them in the new file, replacing ###TEXT### with the content
      for line in lines:
        line = line.replace("###TITLE###", htmlize(section))
        if "Text" in section:
          line = line.replace("###COLOR###", colordic["Text"])
          line = line.replace("###MERKFILE###", merkdic["Text"])
        else:
          try:
            line = line.replace("###COLOR###", colordic[section])
            line = line.replace("###MERKFILE###", merkdic[section])
          except:
            line = line.replace("###COLOR###", "#000066")
            line = line.replace("###MERKFILE###", "merkzeichen-w.jpg")

        self.output += line
        #outfile.write(line)

  def create_body(self, content, section):
    for vorlage in ["Body.txt"]:
      vorfile = codecs.open(HTMLRES_Path + "/"+vorlage, 'r', "utf-8")
      lines = vorfile.readlines()
      vorfile.close()
        #And write them in the new file, replacing ###TEXT### with the content
      for line in lines:
        try:
          line = line.replace("###TEXT###", content) #content.decode('utf-8', errors='ignore')#CODEC PROBLEM!!!
        except UnicodeDecodeError:
          print content
          raise Error
          
        if "Text" in section:
          line = line.replace("###COLOR###", colordic["Text"])
        else:
          try:
            line = line.replace("###COLOR###", colordic[section])
          except:
            line = line.replace("###COLOR###", "#000066")

        self.output += line
        #outfile.write(line)

  def create_footer(self):
  #Write the Footer
    for vorlage in ["Foot.txt"]:
      vorfile = codecs.open(HTMLRES_Path + "/"+vorlage, 'r', "utf-8")
      lines = vorfile.readlines()
      vorfile.close()
      for line in lines:
        self.output += line
        #outfile.write(line)

    self.output += line
    #outfile.close()


  def write_xml(self, xmlfile, sniplist):
    ##This is how an entry in the XML should look like:
    ##'<label index="label_lesson14_item1">phrases before the statement</label>'
    output_file = codecs.open(xmlfile, 'w', "utf-8")
    for item_nr in range(len(sniplist)):
      output_file.write('<label index="label_lesson_'+str(self.lesson_nr)+'_item'+str(item_nr+1)+'">'+sniplist[item_nr]+'</label>\n')
    output_file.close()

  def write_sec_txt(self, content, section):
    section = section.replace('/', '')
    output_file = codecs.open(self.PATH+"lek"+str(self.lesson_nr)+"_"+section+".txt", 'w', "utf-8")
    output_file.write(content)
    output_file.close()

  def write_html(self, filename):
    outfile = codecs.open(filename, 'w', "utf-8")
    outfile.write(self.output)
    outfile.close()
################### //WRITER #######################

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
  input_file = codecs.open(html_file, 'r', "utf-8")
  text = ""
  for line in input_file.readlines():
    text = text + line
  input_file.close()
  return text

def sanitize_snippet(snippet, onlytabs):
  #Clears a line of HTML of some annoying symbols.
  if not onlytabs:
    snippet = snippet.replace('\n',' ')
    snippet = snippet.replace('#','')
    snippet = snippet.strip()
  snippet = snippet.replace('\t','')
  return snippet

def htmlize(content):
  #translates the content from utf-8 to html
  #There's probably a better way...
  content = cgi.escape(content).encode('ascii', 'xmlcharrefreplace')
  
  #content = content.replace("\n", "<br>")
  #content = content.replace(unichr(252), "&uuml;")
  #content = content.replace(unichr(246), "&ouml;")
  #content = content.replace(unichr(214), "&Ouml;")
  #content = content.replace(unichr(220), "&Uuml;")
  #content = content.replace(unichr(223), "&szlig;")
  #content = content.replace(unichr(228), "&auml;")
  #content = content.replace(unichr(196), "&Auml;")

  #content = content.replace(unichr(195169), "&eacute;")

  #content = content.replace(unichr(194180), "\'")
  #content = content.replace(unichr(8222), "\"")
  #content = content.replace(unichr(8221), "\"")
  #content = content.replace(unichr(8220), "\"")
  
  #content = content.replace(unichr(8211), "-")
  #content = content.replace(unichr(8212), "-")

  return content

def run(leclist):
  #dehasher = Dehasher()
  
  #parser = MyHTMLParser()
  #parser.feed(read_html(SRCFILE))
  #snipdic = parser.snipdic
  #writer = Writer(dehasher)
  #writer.create_html(snipdic)
  #writer.write_html()
  #writer.write_xml(XMLFILE, dehasher.inlist)

  #create_directories(leclist)
  convert_to_html(leclist) 
  #for lang in ["en", "sp"]:
  for lesson_nr in leclist:
    PATH = "../lections/lek"+str(lesson_nr)+"/"
    OUTFILE = PATH+"lek"+str(lesson_nr)+"_LL.html"
    path = "../lections/lek" + str(lesson_nr)
    for infile in glob.glob(os.path.join(path, "*lek"+str(lesson_nr)+"*.html")):

      message("processing "+infile)

      parser = MyHTMLParser()
      dehasher = Dehasher(lesson_nr)
      writer = Writer(dehasher, PATH)

      dehasher.inlist = []
      lekpath = "../lections/lek"+str(lesson_nr)+'/'
      parser.feed(read_html(infile))
      snipdic = parser.snipdic
      writer.create_html(snipdic)
      #writer.write_xml("locallang.xml", dehasher.inlist)
      if infile.count('_en.') == 1:
        writer.write_html(lekpath+"lek"+str(lesson_nr)+"_LL.html")

def rerun(lec_nr):
  os.system("rm ../lections/lek"+str(lec_nr)+"/*")
  run([lec_nr])
  
run(range(1,31))