import os
import sys
import subprocess
import monitor
import time


TARGET = "main"
CXX = 'g++'

include_folder = "include"
src_folder = "src"
targer_folder = "target"
build_folder = "build"

makefile_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.abspath(os.path.join(makefile_path, '..'))

def get_src_files():
    return list(filter(lambda src: src[-4:] == ".cpp" or src[-2:] == ".c", os.listdir(os.path.join(project_path, src_folder))))

def get_header_files():
    return list(filter(lambda src: src[-2:] == ".h", os.listdir(os.path.join(project_path, include_folder))))

conn, cur = monitor.init_database(os.path.split(project_path)[1])
added_files_info, _, changed_files_info = monitor.comparison_files_info(monitor.get_files_info(project_path), cur, conn)
changed_files_name = set([os.path.split(path[0])[1] for path in added_files_info] + [os.path.split(path[0])[1] for path in changed_files_info])

src_files = get_src_files()
src_changed_files = list(set(src_files) & changed_files_name)
header_changed_files = list(set(get_header_files()) & changed_files_name)

CXXFLAGS = "-Wall"

operation = sys.argv[1:]

if len(header_changed_files) != 0:
    src_changed_files = src_files
for file_name in src_changed_files:
    form_build_file = "{} {} -c {} -o {} -I {}"
    obj_name = file_name.replace(".cpp", ".o").replace(".c", ".o")
    print(form_build_file.format(CXX, CXXFLAGS, os.path.join(src_folder, file_name), os.path.join(build_folder, obj_name), include_folder))
    resp = subprocess.Popen(form_build_file.format(CXX, CXXFLAGS, os.path.join(project_path, src_folder, file_name), os.path.join(project_path, build_folder, obj_name), os.path.join(project_path, include_folder)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = resp.communicate()
    if len(err) != 0:
        print(err.decode())
        os.utime(os.path.join(project_path, src_folder, file_name), (time.time(), time.time()))