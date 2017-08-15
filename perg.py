#!/bin/python
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("directory")
parser.add_argument("searchterm")
arguments = parser.parse_args();

def walk_folder(folder, searchterm):
    for (dirpath, dirnames, filenames) in os.walk(folder):
        for filename in filenames:
            try:
                filepath = "/".join([dirpath , filename])
                opened = open(filepath)
                str_f = opened.read()
                idx = str_f.find(searchterm)
                if(idx != -1):
                    print "match found at", filepath
            except UnicodeDecodeError:
                print "nontext file"
            except IOError:
                print "IO error"

walk_folder(arguments.directory, arguments.searchterm)
