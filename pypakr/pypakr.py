#!/usr/bin/python

import sys, getopt, os, shutil
import ConfigParser
import os.path, re
import tempfile
import tarfile

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
    - run               - run container (execute script run in the
                          container's virtual environment)
       - Arguments:
         -c, --container <container-directory>

Configuration is in file ~/.pypakr
[Global]
base = /home/george/pypakr/BASE
pypakrdir = /home/george/pypakr
'''
  sys.exit(0)

def containing_directory(path):
  abspath = os.path.abspath(path)
  return os.path.dirname(abspath)

# adjust file
def adjust_file(file, pattern, target, home):
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
  print 'adjust_virtualenv'
  abspath = os.path.abspath(directory)
  bindir = os.path.join(abspath, 'bin')
  pythonpath = os.path.join(bindir, 'python')
  print 'bindir=', bindir
  print 'abspath=', abspath
  adjust_file(os.path.join(bindir, 'activate'),
    'VIRTUAL_ENV=".*"', 'VIRTUAL_ENV="%s"\n', abspath)
  adjust_file(os.path.join(bindir, 'activate.csh'),
    'setenv VIRTUAL_ENV ".*"', 'setenv VIRTUAL_ENV "%s"\n', abspath)
  adjust_file(os.path.join(bindir, 'activate.fish'),
    'set -gx VIRTUAL_ENV ".*"', 'set -gx VIRTUAL_ENV "%s"\n', abspath)
  adjust_file(os.path.join(bindir, '/easy_install'),
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
  # print 'untar %s to %s' % (file, directory)
  tar = tarfile.open(file)
  tar.extractall(path=directory)

def tar(srcdir, dist):
  tf = tarfile.open(dist, 'w')
  pathsave = os.getcwd()
  os.chdir(srcdir)
  l = os.listdir('.')
  # print 'tar: l is', l
  for f in l:
    tf.add(f)
  tf.close()
  os.chdir(pathsave)

def create_install(dir):
  filepath = os.path.join(dir, 'install')
  f = open(filepath, 'w')
  f.write('''#!/bin/sh

./setup
''')
  f.close()
  os.chmod(filepath, 0744)

def command_create_image(base, src, dst, pypakrdir=''):
  if not os.path.exists(src):
    raise Exception('file doesn\'t exist: %s' % src)
  flag_union_created = False
  flag_tmpdir_created = False
  try:
    tmpdir = tempfile.mkdtemp()
    flag_tmpdir_created = True
    print 'tmpdir=', tmpdir
    srcdir = os.path.join(tmpdir, 'SRC')
    print 'srcdir=', srcdir
    os.mkdir(srcdir)
    untar(src, srcdir)
    imgdir = os.path.join(tmpdir, 'IMAGE')
    print 'imgdir=', imgdir
    os.mkdir(imgdir)
    line = 'unionfs -o cow %s=RW:%s=RO %s' % (srcdir, base, imgdir)
    os.system(line)
    flag_union_created = True
    print 'pypakrdir=', pypakrdir
    create_install(imgdir)
    adjust_virtualenv(imgdir)
    line = 'cd %s && vex --path . ./install' % imgdir
    print 'calling', line
    os.system(line)
    print 'calling fusermount'
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

def command_create_container(base, image, container):
  print 'In command_create_container'
  if not os.path.exists(image):
    raise Exception('file doesn\'t exist: %s' % image)
  if (image == None) or (container == None):
    usage()
  flag_container_created = False
  flag_tmpdir_created = False
  try:
    os.mkdir(container)
    flag_container_created = True
    os.system('cp -R %s/* %s' % (base, container))
    tmpdir = tempfile.mkdtemp()
    flag_tmpdir_created = True
    print 'tmpdir=', tmpdir
    imgdir = '%s/IMAGE' % tmpdir
    print 'imgdir=', imgdir
    os.mkdir(imgdir)
    untar(image, imgdir)
    os.system('cp -R %s/* %s' % (imgdir, container))
    adjust_virtualenv(container)
  except Exception as ex:
    if flag_tmpdir_created:
      os.system('rm -rf %s' % tmpdir)
    if flag_container_created:
      os.system('rm -rf %s' % container)
    raise ex

def command_init(base):
  os.system('vex --make --path %s' % base)

def command_run(container):
  if container == None:
    usage()
  print 'container=', container
  if (not os.path.exists(container)) or (not os.path.isdir(container)):
    raise Exception('%s is not a directory' % container)
  os.system('cd %s && vex --path . ./run' % container)
