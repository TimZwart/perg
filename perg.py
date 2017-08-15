#!/bin/python
import os
import argparse
import pdb

parser = argparse.ArgumentParser()
parser.add_argument("directory")
parser.add_argument("searchterm")
arguments = parser.parse_args();

script_dir = os.path.dirname(os.path.realpath(__file__))
exclude_filename = "exclude.perg"

exclude_filepath =  "/".join([script_dir, exclude_filename])
with open(exclude_filepath) as exclude_file :
    exclude_lines = exclude_file.readlines()
excludes = map(str.strip, exclude_lines)

excluded_extensions_filename = "excluded_extensions.perg"
excluded_extensions_filepath = "/".join([script_dir, excluded_extensions_filename])
with open(excluded_extensions_filepath) as excluded_extensions_file :
    excluded_extensions_lines = excluded_extensions_file.readlines()
excluded_extensions = map(str.strip, excluded_extensions_lines)

def walk_folder(folder, searchterm):
    matchesFound = False
    for (dirpath, dirnames, filenames) in os.walk(folder):
        for filename in filenames:
            dirs = dirpath.split("/")
            intersec = [x for x in dirs if x in excludes]
            filename_parts = filename.split(".")
#            pdb.set_trace()
            if intersec == [] and (len(filename_parts) == 1 or filename_parts[-1] not in excluded_extensions):
                try:
                    filepath = "/".join([dirpath , filename])
                    opened = open(filepath)
                    str_f = opened.read()
                    idx = str_f.find(searchterm)
                    if idx != -1:
                        print filepath
                        matchesFound = True
                except UnicodeDecodeError:
                    print "nontext file"
                except IOError:
                    print "IO error"
            elif intersec is None:
                print "error intersection list is None"
    if not matchesFound:
        print "no matches found"

walk_folder(arguments.directory, arguments.searchterm)
