#!/bin/python
import os
import argparse
import pdb
from functools import reduce

parser = argparse.ArgumentParser()
parser.add_argument("directory")
parser.add_argument("searchterm")
arguments = parser.parse_args();

script_dir = os.path.dirname(os.path.realpath(__file__))

exclude_filename = "exclude.perg"
exclude_filepath =  "/".join([script_dir, exclude_filename])
with open(exclude_filepath) as exclude_file :
    exclude_lines = exclude_file.readlines()
exclude_list = map(str.strip, exclude_lines)
excludes = set(exclude_list)

excluded_extensions_filename = "excluded_extensions.perg"
excluded_extensions_filepath = "/".join([script_dir, excluded_extensions_filename])
with open(excluded_extensions_filepath) as excluded_extensions_file :
    excluded_extensions_lines = excluded_extensions_file.readlines()
excluded_extensions = map(str.strip, excluded_extensions_lines)

#get standard directories to search
default_search_directories_filename = "default_search_directories.perg"
default_search_directories_filepath = "/".join([script_dir, default_search_directories_filename]) 
with open(default_search_directories_filepath) as defeault_search_directories_file:
    default_search_directories_lines = defeault_search_directories_file.readlines()
default_search_directories = map(str.strip, default_search_directories_lines) 

search_directories_raw = default_search_directories + [arguments.directory]
search_directories_fullpath = map(os.path.abspath, search_directories_raw)
search_directories = list(set(search_directories_fullpath))

def walk_folder(folder, searchterm):
    print "Searching folder", folder
    matchesFound = False
    for (dirpath, dirnames, filenames) in os.walk(folder):
        dirnames[:] = [d for d in dirnames if not (d in excludes)]
        for filename in filenames:
            dirs = dirpath.split("/")
            filename_parts = filename.split(".")
#            pdb.set_trace()
            if len(filename_parts) == 1 or filename_parts[-1] not in excluded_extensions:
                try:
                    filepath = "/".join([dirpath , filename])
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
                except UnicodeDecodeError:
                    print "nontext file"
                except IOError:
                    print "IO error"
    return matchesFound

print "Searchterm: ", arguments.searchterm
foundResults = map((lambda x: walk_folder(x, arguments.searchterm)), search_directories)
matchesFound = reduce((lambda x,y: x or y), foundResults)

if not matchesFound:
    print "no matches found"
