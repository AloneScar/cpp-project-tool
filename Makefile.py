import os
import sys
import subprocess
import monitor
import time
import shutil
import platform


TARGET = "main"
CXX = 'g++'

include_folder = "include"
src_folder = "src"
target_folder = "target"
build_folder = "build"

makefile_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.abspath(os.path.join(makefile_path, '..'))

def get_src_files():
    return list(filter(lambda src: src[-4:] == ".cpp" or src[-2:] == ".c", os.listdir(os.path.join(project_path, src_folder))))

def get_build_files():
    return list(filter(lambda obj: obj[-2:] == ".o", os.listdir(os.path.join(project_path, build_folder))))

def get_header_files():
    return list(filter(lambda src: src[-2:] == ".h", os.listdir(os.path.join(project_path, include_folder))))

CXXFLAGS = "-Wall"

operation = sys.argv[1:]

def build():
    conn, cur = monitor.init_database(os.path.split(project_path)[1])
    added_files_info, _, changed_files_info = monitor.monitor_global(monitor.get_files_info(project_path), cur, conn)
    changed_files_name = set([os.path.split(path[0])[1] for path in changed_files_info + added_files_info])

    src_files = get_src_files()
    build_files = get_build_files()
    src_changed_files = list(set(src_files) & changed_files_name)
    header_changed_files = list(set(get_header_files()) & changed_files_name)

    # if the file in src, but not in build, then add to src_changed_files
    for src_name in src_files:
        obj_name = src_name.replace(".cpp", ".o").replace(".c", ".o")
        if obj_name not in build_files and src_name not in src_changed_files:
            src_changed_files.append(src_name)
    # if the header_files changed, all the file in src need to rebuild
    if len(header_changed_files) != 0:
        src_changed_files = src_files
    for file_name in src_changed_files:
        form_build_file = '{} {} -c "{}" -o "{}" -I {}'
        obj_name = file_name.replace(".cpp", ".o").replace(".c", ".o")
        print(form_build_file.format(CXX, CXXFLAGS, os.path.join(src_folder, file_name), os.path.join(build_folder, obj_name), include_folder))
        resp = subprocess.Popen(form_build_file.format(CXX, CXXFLAGS, os.path.join(project_path, src_folder, file_name), os.path.join(project_path, build_folder, obj_name), os.path.join(project_path, include_folder)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = resp.communicate()
        if len(out) != 0:
            print(out.decode('gbk'))
        if len(err) != 0:
            print(err.decode('gbk'))
            os.utime(os.path.join(project_path, src_folder, file_name), (time.time(), time.time()))
    
    # to create TARGET file
    added_files_info, _, changed_files_info = monitor.monitor_folder(monitor.get_files_info(os.path.join(project_path, build_folder)), cur, conn)
    build_changed_files = set([os.path.split(path[0])[1] for path in changed_files_info + added_files_info])

    if len(build_changed_files) != 0:
        to_build_files = " ".join(["%s/" % build_folder + build_file for build_file in build_changed_files])
        form_target_file = '{} "{}" -o "{}"'
        print(form_target_file.format(CXX, to_build_files, TARGET))
        resp = subprocess.Popen(form_target_file.format(CXX, to_build_files, os.path.join(project_path, targer_folder, TARGET)), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = resp.communicate()
        if len(out) != 0:
            print(out.decode('gbk'))
        if len(err) != 0:
            print(err.decode('gbk'))
    

def init():
    for dir in [build_folder, src_folder, include_folder, targer_folder]:
        try:
            os.mkdir(os.path.join(project_path, dir))
        except:
            pass
    with open(mode="w", file=os.path.join(project_path, 'src', 'main.cpp')) as f:
        f.write(
'''#include <iostream>
using namespace std;

int main()
{
    cout << "Hello World" << endl;
    return 0;
}
'''
        )

def restore():
    for dir in ['build', 'src', 'target', 'include']:
        try:
            shutil.rmtree(os.path.join(project_path, dir))
        except:
            pass

def run():
    to_target_path = os.path.join(project_path, target_folder, TARGET)
    system_type = platform.system()
    if system_type == 'Linux':
        to_target_path = "/".join(['"' + path + '"' for path in to_target_path.split('/')])

    resp = subprocess.Popen(to_target_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = resp.communicate()
    if len(out) != 0:
        print(out.decode('gbk'))
    if len(err) != 0:
        print(err.decode('gbk'))
    

if len(operation) == 0:
    operation = None
else:
    operation = operation[0]
if operation == None:
    build()
elif operation == 'init':
    init()
elif operation == 'restore':
    restore()
elif operation == 'run':
    run()
