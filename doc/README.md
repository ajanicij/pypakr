# Creating source directory

We are going to go through the process of creating a custom container, from
a source directory all the way to a container directory.

Let's start from a package jokes that we are going to use to create a
container. We create a directory JOKES with the following contents:

```
./setup
./run
./packages
./packages/jokes
./packages/jokes/setup.py
./packages/jokes/jokes
./packages/jokes/jokes/__init__.pyc
./packages/jokes/jokes/__init__.py
./packages/funniest
./packages/funniest/setup.py
./packages/funniest/funniest
./packages/funniest/funniest/__init__.py
./run.py
```

Change into this directory:

    cd JOKES

Now create a tar file with the whole contents of this directory:

    tar cvf JOKES.tar *

And that gives us a source file that is the starting point. Move this
file outside of JOKES directory:

    mv JOKES.tar ..

The first step is to create an image file:

    pypakr create-image -s JOKES.tar -i JOKESIMAGE.tar

```
(ENV) aleks@aleks-HP-EliteDesk-800-G1-TWR:~/Work/pypakr/ENV$ pypakr create-image -s JOKES.tar -i JOKESIMAGE.tar
Processing ./packages/jokes
Building wheels for collected packages: jokes
  Running setup.py bdist_wheel for jokes ... done
  Stored in directory: /tmp/pip-ephem-wheel-cache-yJoR6g/wheels/e2/61/ae/18f60225634b429273156b88007fb6f267e0df0d25e0d27a61
Successfully built jokes
Installing collected packages: jokes
Successfully installed jokes-0.1
```

That created an image file JOKESIMAGE.tar that contains a full information
needed to created a container.

Now we can create a container:

    pypakr create-container -i JOKESIMAGE.tar -c JOKESCONT

That created a directory JOKESCONT that looks just like what
virtualenv-created virtual environment into which we installed our package
jokes.

Now we can activate this environment:

```
cd JOKESCONT
source bin/activate
python run.py

Q. What do you do with a sick boat?
A. TAKE IT TO THE DOC!

```

File run.py that we used for this looks like this:

```
import jokes

print jokes.random()
```

That shows that our package jokes in installed.

Another way to run things in a container is to execute script run in a
virtual environment, in a subprocess so that our environment doesn't
have to be activated and deactivated:

```
pypakr run -c JOKESCONT -r ./run

Q. Why did the blonde stare at a frozen orange juice can for 2 hours?
A. Because it said "concentrate"!
```
