#!/usr/bin/python

import sys, getopt, os, shutil
import ConfigParser
import os.path, re
import tempfile
import tarfile
import distutils.core

def usage():
  print '''
pypakr
Python containers
Usage:
pypakr <command> <parameters>
  - Commands:
    - init              - initialize
    - create-image      - create image
       - Arguments:
         -s, --src <source-file>
         -i, --image <image-file>
    - create-container  - create container
       - Arguments:
         -i, --image <image-file>
         -c, --container <container-directory>
    - run               - run container (execute script in the
                          container's virtual environment)
       - Arguments:
         -c, --container <container-directory>
         -r, --script <script-to-execute>

Configuration is in file ~/.pypakr
[Global]
base = /home/george/pypakr/BASE
'''
  sys.exit(0)

def get_config_path():
  'Return the path of .pypakr file.'
  home = os.environ['HOME']
  config_path = os.path.join(home, '.pypakr')
  return config_path

def get_base():
  'Returns the path of virtualenv base directory.'
  config = ConfigParser.RawConfigParser()
  config_path = get_config_path()
  config.read(config_path)
  base = config.get('Global', 'base')
  return base

def create_base():
  'Checks if .pypakr exists in home directory and creates it if it doesn\'t.'
  config_path = get_config_path()
  home = os.environ['HOME']
  if not os.path.isfile(config_path):
    f = open(config_path, 'w')
    f.write('[Global]' + os.linesep)
    f.write(('base = %s' % os.path.join(home, 'pypakr', 'BASE')) +
      os.linesep)
    f.close()

def containing_directory(path):
  'Returns the directory that the path is in.'
  abspath = os.path.abspath(path)
  return os.path.dirname(abspath)

# adjust file
def adjust_file(file, pattern, target, home):
  '''Adjusts a file by replacing all lines that match the pattern with
     a line constructed from target and specified home directory.'''
  outfile = file + '.tmp'
  mode = os.stat(file).st_mode
  with open(file) as f:
    with open(outfile, 'w') as outf:
      for line in f:
        if re.match(pattern, line):
          out_line = target % home
        else:
          out_line = line
        outf.write(out_line)
  os.rename(outfile, file)
  # Set file mode to the same value as the original.
  os.chmod(file, mode)

def adjust_virtualenv(directory):
  '''Adjust a precise set of scripts in virtual environment\'s bin
     directory according to the virtual environment\'s current location.'''
  # print 'adjust_virtualenv'
  abspath = os.path.abspath(directory)
  bindir = os.path.join(abspath, 'bin')
  pythonpath = os.path.join(bindir, 'python')
  # print 'bindir=', bindir
  # print 'abspath=', abspath
  adjust_file(os.path.join(bindir, 'activate'),
    'VIRTUAL_ENV=".*"', 'VIRTUAL_ENV="%s"\n', abspath)
  adjust_file(os.path.join(bindir, 'activate.csh'),
    'setenv VIRTUAL_ENV ".*"', 'setenv VIRTUAL_ENV "%s"\n', abspath)
  adjust_file(os.path.join(bindir, 'activate.fish'),
    'set -gx VIRTUAL_ENV ".*"', 'set -gx VIRTUAL_ENV "%s"\n', abspath)
  adjust_file(os.path.join(bindir, 'easy_install'),
    '#!/.*', '#!%s\n', pythonpath)
  adjust_file(os.path.join(bindir, 'easy_install-2.7'),
    '#!/.*', '#!%s\n', pythonpath )
  adjust_file(os.path.join(bindir, 'pip'),
    '#!/.*', '#!%s\n', pythonpath)
  adjust_file(os.path.join(bindir, 'pip2'),
    '#!/.*', '#!%s\n', pythonpath)
  adjust_file(os.path.join(bindir, 'pip2.7'),
    '#!/.*', '#!%s\n', pythonpath)
  adjust_file(os.path.join(bindir, 'python-config'),
    '#!/.*', '#!%s\n', pythonpath)
  adjust_file(os.path.join(bindir, 'wheel'),
    '#!/.*', '#!%s\n', pythonpath)

def untar(file, directory):
  'Untar a specified tar file into specified directory.'
  tar = tarfile.open(file)
  tar.extractall(path=directory)
  tar.close()

def tar(srcdir, dist):
  '''Tar all files and directories in the specified source directory and
     write to the specified path.'''
  tf = tarfile.open(dist, 'w')
  flag_chdir = False
  try:
    pathsave = os.getcwd()
    os.chdir(srcdir)
    flag_chdir = True
    l = os.listdir('.')
    # print 'tar: l is', l
    for f in l:
      tf.add(f)
  finally:
    tf.close()
  if flag_chdir:
    os.chdir(pathsave)

def create_install(dir):
  'Create install script in the specified directory.'
  filepath = os.path.join(dir, 'install')
  f = open(filepath, 'w')
  f.write('''#!/bin/sh

./setup
''')
  f.close()
  os.chmod(filepath, 0744)

def create_image(base, src, dst):
  'Create image file.'
  if not os.path.exists(src):
    raise Exception('file doesn\'t exist: %s' % src)
  flag_union_created = False
  flag_tmpdir_created = False
  try:
    tmpdir = tempfile.mkdtemp()
    flag_tmpdir_created = True
    # print 'tmpdir=', tmpdir
    srcdir = os.path.join(tmpdir, 'SRC')
    # print 'srcdir=', srcdir
    os.mkdir(srcdir)
    untar(src, srcdir)
    imgdir = os.path.join(tmpdir, 'IMAGE')
    # print 'imgdir=', imgdir
    os.mkdir(imgdir)
    line = 'unionfs -o cow %s=RW:%s=RO %s' % (srcdir, base, imgdir)
    os.system(line)
    flag_union_created = True
    create_install(imgdir)
    adjust_virtualenv(imgdir)
    line = 'cd %s && vex --path . ./install' % imgdir
    # print 'calling', line
    os.system(line)
    # print 'calling fusermount'
    os.system('fusermount -u %s' % imgdir)
    flag_union_created = False
    tar(srcdir, dst)
    # os.system('rm -rf %s' % tmpdir)
    shutil.rmtree(tmpdir)
  except Exception as ex:
    if flag_union_created:
      os.system('fusermount -u %s' % imgdir)
    if flag_tmpdir_created:
      # os.system('rm -rf %s' % tmpdir)
      shutil.rmtree(tmpdir)
    raise ex

def command_create_image(src, dst):
  'Execute pypakr create-image.'
  base = get_base()
  create_image(base, src, dst)

def copytree(src, dst):
  '''
  Copy directory src to dst.
  How it differs from shutil.copytree: it works if directory dst
  exists.
  How it differs from distutils.dir_util.copy_tree: it is much faster.
  The version of command_create_container with distutils.dir_util.copy_tree
  takes from 48s to 1m 16s, compared to 7s with cp -R ...
  '''
  os.system('cp -R %s/* %s' % (src, dst))

def create_container(base, image, container):
  'Create container.'
  if not os.path.exists(image):
    raise Exception('file doesn\'t exist: %s' % image)
  if (image == None) or (container == None):
    usage()
  flag_container_created = False
  flag_tmpdir_created = False
  try:
    # print 'mkdir ', container
    os.mkdir(container)
    flag_container_created = True
    copytree(base, container)
    # shutil.copytree(base, container)
    # distutils.dir_util.copy_tree(base, container)
    tmpdir = tempfile.mkdtemp()
    flag_tmpdir_created = True
    imgdir = os.path.join(tmpdir, 'IMAGE')
    os.mkdir(imgdir)
    untar(image, imgdir)
    copytree(imgdir, container)
    # shutil.copytree(imgdir, container)
    # distutils.dir_util.copy_tree(imgdir, container)
    adjust_virtualenv(container)
    shutil.rmtree(tmpdir)
  except Exception as ex:
    if flag_tmpdir_created:
      # os.system('rm -rf %s' % tmpdir)
      shutil.rmtree(tmpdir)
    if flag_container_created:
      # os.system('rm -rf %s' % container)
      shutil.rmtree(container)
    raise ex

def command_create_container(image, container):
  'Execute command pypakr create-container.'
  base = get_base()
  create_container(base, image, container)

def init(base):
  'Initialize pypakr.'
  os.system('virtualenv %s' % base)

def command_init():
  'Execute command pypakr init.'
  create_base()
  base = get_base()
  init(base)

def run(container, script):
  'Run specified script in the specified container.'
  if container == None:
    usage()
  # print 'container=', container
  if (not os.path.exists(container)) or (not os.path.isdir(container)):
    raise Exception('%s is not a directory' % container)
  os.system('cd %s && vex --path . %s' % (container, script))

def command_run(container, script):
  'Execute command pypakr run.'
  run(container, script)
