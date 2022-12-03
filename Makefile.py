import os
import sys
import subprocess


TARGET = "main"
CXX = 'g++'

INCLUDE_DIR = "./include"
SRC_DIR = "./src"
TARGET_DIR = "./target"
BUILD_DIR = "./build"

def get_src_files():
    return list(filter(lambda src: src[-4:] == ".cpp" or src[-2:] == ".c", os.listdir(SRC_DIR)))
    

def get_obj_files():
    return [i.replace(".cpp", ".o").replace(".c", ".o") for i in get_src_files()]

SRCS = get_src_files()
OBJS = get_obj_files()

CXXFLAGS = "-Wall"

operation = sys.argv[1:]

print(OBJS)
print(SRCS)

if len(operation) == 0:
    resp = subprocess.Popen("{} {} -c {} -o {}".format(CXX, CXXFLAGS, SRCS, OBJS), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(resp.stdout.read())
