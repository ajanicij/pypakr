# pypakr

Python containers for virtualenv

This Python project implements simple containers in the sense similar to
Docker: you can generate an image file that contains complete information
needed to create a virtual environment on any system that has pypakr
installed. NOTE: don't confuse this with the other meaning of the term
container, which is "a holder object that stores a collection of other
objects (its elements)." [http://www.cplusplus.com/reference/stl/]

## Introduction

Just like Docker can run isolated environments, called containers,
Python has virtualenv. This tool creates isolated Python
environments. But it misses what Docker has, which is a way to have a file
that somehow defines the environment and that can be used to create a
virtual environment on any machine that has Docker installed.

In Docker, containers are created from "images" that specify their precise
contents (source: Wikipedia). We need something like that for Python.

pypakr fulfills that need. It can take a description of which Python
packages need to be installed and use it to generate an image file that
describes what is installed in a virtual environment. Then it can take that
image and generate a directory that contains a complete virtual environment.

This can be done with Docker too. The advantage of pypakr is that the images
are much smaller - they contain only Python files that can be overlaid
on top of a generic virtual environment to produce a "container" that can
run a Python application or microservice. Containers are also smaller than
a typical Docker container, because they only contain a virtualenv-style
environment.

## Dependencies

pypakr currently runs on Linux, and other than Python, it depends on the
following software:

- virtualenv
- vex, for running code in a virtual environment from a script
- unionfs-fuse, for mounting UnionFS volumes

Install these tools like this:

    pip install virtualenv
    pip install vex

On Ubuntu, install unionfs-fuse like this:

    sudo apt-get install unionfs-fuse

## Testing

pypakr can be tested before installing by running

    tox

or after installing by running

    pytest

## Installation

Run

    pip install pypakr

## Initialization

After you installed pypakr, run command

    pypakr init

It will create configuration file .pypakr in your home directory and
also create a base virtual environment in directory

    $HOME/pypakr/BASE

By default, if .pypakr does not exist before you run pypakr init, it
will be created to look like this:

```
[Global]
base = /home/george/pypakr/BASE
```
where /home/george stands for your home directory.

However, if you don't like this default, create .pypakr and set value of
key base to point to some other path. Then run pypakr init, and it will
try to create the base directory if it doesn't exist and then create
a virtual environment in it.

# Help

Run pypakr by itself on the command line to get help, or

    pypakr help

It will give you text like this:

```
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
```

See documentation in directory doc. As a quick reminder, here are the steps
to create a container:

1. Create source file CUSTOM.tar.

2. Create image file IMAGE.tar:

    pypakr create-image -s CUSTOM.tar -i IMAGE.tar

3. Create container CONT:

    pypakr create-container -i IMAGE.tar -c CONT

4. Run script run in the container CONT:

    pypakr run -c CONT -r ./run

# TODO

This project is still young and there is so much more that can be done.
Here are some ideas:

- Port to Windows. unionfs is a Linux thing; a Windows version of pypakr
is possible, by generating a custom virtual environment and then extracting
the difference from the base virtual environment and tarring that to create
an image.
- A hub site like Docker Hub.
- Serverless web application that uses pypakr containers as units of
functionality.

# Contributions

All comments, questions, issue reports, and pull requests are welcome!
