#!/bin/python
import os
import argparse
import pdb
import zipfile
import shutil
from functools import reduce
from binaryornot.check import is_binary

parser = argparse.ArgumentParser()
parser.add_argument("directory")
parser.add_argument("searchterm")
arguments = parser.parse_args();

script_dir = os.path.dirname(os.path.realpath(__file__))

exclude_filename = "exclude.perg"
exclude_filepath =  "/".join([script_dir, exclude_filename])
with open(exclude_filepath) as exclude_file :
    exclude_lines = exclude_file.readlines()
raw_exclude_list = map(str.strip, exclude_lines)
exclude_list = [d for d in raw_exclude_list if not d.startswith('#')]
excludes = set(exclude_list)

excluded_extensions_filename = "excluded_extensions.perg"
excluded_extensions_filepath = "/".join([script_dir, excluded_extensions_filename])
with open(excluded_extensions_filepath) as excluded_extensions_file :
    excluded_extensions_lines = excluded_extensions_file.readlines()
raw_excluded_extensions = map(str.strip, excluded_extensions_lines)
excluded_extensions =[d for d in raw_excluded_extensions if not d.startswith('#')] 

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

def searchZipFile(dirpath, filename):
    #unzip it
    matchesFound = False
    print "unzipping ", filename
    zip_ref = zipfile.ZipFile(filepath, 'r')
    unzipped_name = filename+"#"
    unzipped_path = "/".join([dirpath, unzipped_name])
    zip_ref.extractall(unzipped_path)
    zip_ref.close()
    matchesFound = walk_folder(unzipped_path, searchterm, False) or matchesFound
    shutil.rmtree(unzipped_path) #delete after we're done

def searchFile(filepath):
    opened = open(filepath)
    str_f = opened.read()
    idx = str_f.find(searchterm)
    if idx != -1:
        print filepath
        matchesFound = True
        f_lines = str_f.split('\n')
        matching_lines = [l for l in f_lines if l.find(searchterm) != -1]
        for m in matching_lines:
            print "    ", m
    else:
        if filename.find(searchterm) != -1:
            print filepath

def inner_loop(dirpath, filename):
    matchesFound = False
    if dirpath == "/cygdrive/c/Users/tim.zwart/Downloads/INGEX_Core":
        pdb.set_trace()
    filename_parts = filename.split(".")
    filepath = "/".join([dirpath , filename])
    if len(filename_parts) == 1 or filename_parts[-1] not in excluded_extensions:
#      print "filename", filename
#      print "last in filename_parts", filename_parts[-1]
       if filename_parts[-1] in zip_extensions:
            matchesFound = searchZipFile(dirpath, filename) or matchesFound
       else:
         try:
           if is_binary(filepath):
             break
           searchFile(filepath)
         except UnicodeDecodeError:
             print "nontext file"
         except IOError:
             print "IO error"
      return matchesFound


def walk_folder(folder, searchterm, includefirstline = True):
    print "walk_folder called, folder=", folder
    if includefirstline:
        print "Searching folder", folder
    matchesFound = False
    match_lines = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        print "dirpath ", dirpath
        print "walking files, ", filenames
        dirnames[:] = [d for d in dirnames if not (d in excludes)]
        for filename in filenames:
            matchesFound |= inner_loop
    return matchesFound

print "Searchterm: ", arguments.searchterm
foundResults = map((lambda x: walk_folder(x, arguments.searchterm)), search_directories)
matchesFound = reduce((lambda x,y: x or y), foundResults)

if not matchesFound:
    print "no matches found"
