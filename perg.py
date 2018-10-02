#!/bin/python
import os
import argparse
import pdb
import zipfile
import shutil
import cProfile
import pstats
import subprocess
from functools import reduce
from binaryornot.check import is_binary

try: 
    os.remove("perg_comparisons")
    os.remove("perglog")
except:
    pass

profile = cProfile.Profile()
profile.enable()

parser = argparse.ArgumentParser()
parser.add_argument("directory")
parser.add_argument("searchterm")
parser.add_argument("switch")
arguments = parser.parse_args();

script_dir = os.path.dirname(os.path.realpath(__file__))

exclude_filename = "exclude.perg"
exclude_filepath =  "/".join([script_dir, exclude_filename])
with open(exclude_filepath) as exclude_file :
    exclude_lines = exclude_file.readlines()
raw_exclude_list = map(str.strip, exclude_lines)
exclude_list = [d for d in raw_exclude_list if not d.startswith('#')]
excludes = set(exclude_list)

print "excluded paths are", excludes

excluded_extensions_filename = "excluded_extensions.perg"
excluded_extensions_filepath = "/".join([script_dir, excluded_extensions_filename])
with open(excluded_extensions_filepath) as excluded_extensions_file :
    excluded_extensions_lines = excluded_extensions_file.readlines()
raw_excluded_extensions = map(str.strip, excluded_extensions_lines)
excluded_extensions =[d for d in raw_excluded_extensions if not d.startswith('#')] 

print "excluded_extensions are ", excluded_extensions

allowed_extensions = ['java', 'class', 'js', 'jar', 'zip', 'py', 'log', 'vim']

print "allowed_extensions are ", allowed_extensions

#get standard directories to search
default_search_directories_filename = "default_search_directories.perg"
default_search_directories_filepath = "/".join([script_dir, default_search_directories_filename]) 
with open(default_search_directories_filepath) as defeault_search_directories_file:
    default_search_directories_lines = defeault_search_directories_file.readlines()
not_commented_searchdir_lines = [d for d in default_search_directories_lines if not d.startswith('#')]
default_search_directories = map(str.strip, not_commented_searchdir_lines) 

search_directories_raw = default_search_directories + [arguments.directory]
search_directories_fullpath = map(os.path.abspath, search_directories_raw)
search_directories = list(set(search_directories_fullpath))

zip_extensions = ['zip', 'jar', 'war']

ONLY_FILENAMES = True if arguments.switch.find("f") != -1 else False
SEARCH_ZIP_FILES = True if arguments.switch.find("z") != -1 else False
NOWHITELIST = True if arguments.switch.find("nw") != -1 else False


def searchZipFile(dirpath, filename, filepath, searchterm):
    #unzip it
    matchesFound = False
    try:
      zip_ref = zipfile.ZipFile(filepath, 'r')
      unzipped_name = filename+"#"
      unzipped_path = "/".join([dirpath, unzipped_name])
      zip_ref.extractall(unzipped_path)
      zip_ref.close()
      matchesFound = walk_folder(unzipped_path, searchterm, False) or matchesFound
      shutil.rmtree(unzipped_path) #delete after we're done
    except zipfile.BadZipfile:
      print "BAD ZIP FILE", filepath
    return matchesFound

def filenameSearch(filepath, filename, searchterm):
   f1 = open("perg_comparisons", "a+")
   f1.write("comparing "+filepath+" with "+searchterm+"\n")
   f1.close()
#   if filename == "SamlAuthenticationHandler.class":
#       pdb.set_trace()
   if findi(filename, searchterm) != -1:
       print filepath
       return True
   return False

def decompileIfJvm(filepath, filename , searchterm):
    winpath = subprocess.check_output(['cygpath', '-w', filepath])
    decompiled_string = subprocess.check_output(['jd-cli', winpath])
    return searchFileString(decompiled_string, filepath, searchterm)

def searchFileString(str_f, filepath, searchterm):
    matchesFound = False
    strfilecaps = str_f.capitalize()
    idx = findi(strfilecaps, searchterm)
    if idx != -1:
        if not matchesFound:
            print filepath
        matchesFound = True
        f_lines = str_f.split('\n')
        matching_lines = [l for l in f_lines if findi(l, searchterm) != -1]
        for m in matching_lines:
            print "    ", m
    return matchesFound


def searchFile(filepath, filename, searchterm, file_extension):
    matchesFound = False
    matchesFound = filenameSearch(filepath, filename, searchterm) 
    if (ONLY_FILENAMES):
      return matchesFound
    #check if its a java class file, if so decompile it
    if file_extension == 'class': 
        matchesFound = decompileIfJvm(filepath, filename, searchterm) or matchesFound  
    else:
        if is_binary(filepath):
          return matchesFound
        opened = open(filepath)
        str_f = opened.read()
        matchesFound = searchFileString(str_f, filepath, searchterm) or matchesFound
    if matchesFound:
        return True
    else:
        return filenameSearch(filepath, filename, searchterm)

def findi(string, term):
    cString = string.upper()
    cTerm = term.upper()
    return cString.find(cTerm)

def inner_loop(dirpath, filename, searchterm):
    matchesFound = False
    filename_parts = filename.split(".")
    filepath = "/".join([dirpath , filename])
    file_extension = filename_parts[-1]
    if (len(filename_parts) == 1 or file_extension not in excluded_extensions) and (filename_parts[-1] in allowed_extensions or NOWHITELIST):
       if file_extension in zip_extensions and SEARCH_ZIP_FILES:
            matchesFound = searchZipFile(dirpath, filename, filepath, searchterm) or matchesFound
       else:
         try:
           matchesFound = searchFile(filepath, filename, searchterm, file_extension) or matchesFound
         except UnicodeDecodeError:
             print "nontext file"
         except IOError:
             print "IO error"
    return matchesFound


def walk_folder(folder, searchterm, includefirstline = True):
    #print "walk_folder called, folder=", folder
    if includefirstline:
        print "Searching folder", folder
    matchesFound = False
    match_lines = []

    for (dirpath, dirnames, filenames) in os.walk(folder):
        f1 = open('./perglog', 'a+')
        f1.write("dirpath "+ dirpath + "\n")
        f1.write("walking files: "+ ",".join(filenames) +"\n")
        f1.close()
        dirnames[:] = [d for d in dirnames if not (d in excludes)]
        for filename in filenames:
            matchesFound = inner_loop(dirpath, filename, searchterm)
    return matchesFound

print "Searchterm: ", arguments.searchterm
foundResults = map((lambda x: walk_folder(x, arguments.searchterm)), search_directories)
matchesFound = reduce((lambda x,y: x or y), foundResults)

if not matchesFound:
    print "no matches found"

profile.disable()
#profile.print_stats()
