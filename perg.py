#!/bin/python
import os
import argparse
import pdb
import zipfile
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

def walk_folder(folder, searchterm, includefirstline = True):
    if includefirstline:
        print "Searching folder", folder
    matchesFound = False
    for (dirpath, dirnames, filenames) in os.walk(folder):
        dirnames[:] = [d for d in dirnames if not (d in excludes)]
        for filename in filenames:
            dirs = dirpath.split("/")
            filename_parts = filename.split(".")
#           pdb.set_trace()
            if len(filename_parts) == 1 or filename_parts[-1] not in excluded_extensions:
                if(filename_parts[-1] in zip_extensions:
                  #unzip it
                  zip_ref = zipfile.Zipfile(filename, 'r')
                  unzipped_name = filename+"#" 
                  zip_ref.extractall(unzipped_name)
                  zip_ref.close()
                  walk_folder(unzipped_name, searchterm, False)
                  shutil.rmtree(unzipped_name) #delete after we're done
                try:
                    filepath = "/".join([dirpath , filename])
                    if is_binary(filepath):
                        break
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
