# Introduction

We are going to build image and container for a Flask application.

We will use the most basic sample from Flask's website:

```
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
```

Put that into file hello.py. We also need file setup:

pip install Flask

Make setup executable, because it will be run as a shell script to install
Flask.

And the final file is run; make that executable too:

```
#!/bin/sh

FLASK_APP=hello.py python -m flask run
```

Create a tar file with hello.py, run and setup:

    tar cvf FLASK.tar hello.py run setup

Now the steps are the same as in the basic example, with different file
and directory names:

```
$ pypakr create-image -s FLASK.tar -i FLASKIMAGE.tar
Collecting Flask
  Using cached https://files.pythonhosted.org/packages/7f/e7/08578774ed4536d3242b14dacb4696386634607af824ea997202cd0edb4b/Flask-1.0.2-py2.py3-none-any.whl
Collecting Werkzeug>=0.14 (from Flask)
  Using cached https://files.pythonhosted.org/packages/20/c4/12e3e56473e52375aa29c4764e70d1b8f3efa6682bef8d0aae04fe335243/Werkzeug-0.14.1-py2.py3-none-any.whl
Collecting click>=5.1 (from Flask)
  Using cached https://files.pythonhosted.org/packages/fa/37/45185cb5abbc30d7257104c434fe0b07e5a195a6847506c074527aa599ec/Click-7.0-py2.py3-none-any.whl
Collecting Jinja2>=2.10 (from Flask)
  Using cached https://files.pythonhosted.org/packages/7f/ff/ae64bacdfc95f27a016a7bed8e8686763ba4d277a78ca76f32659220a731/Jinja2-2.10-py2.py3-none-any.whl
Collecting itsdangerous>=0.24 (from Flask)
  Using cached https://files.pythonhosted.org/packages/c9/c3/8dadb353944803796515ce68ad3944e6e7acc934f5036c40829cb96e64a1/ItsDangerous-1.0.0-py2.py3-none-any.whl
Collecting MarkupSafe>=0.23 (from Jinja2>=2.10->Flask)
Installing collected packages: Werkzeug, click, MarkupSafe, Jinja2, itsdangerous, Flask
Successfully installed Flask-1.0.2 Jinja2-2.10 MarkupSafe-1.0 Werkzeug-0.14.1 click-7.0 itsdangerous-1.0.0

$ pypakr create-container -i FLASKIMAGE.tar -c FLASKCONT
$ pypakr run -c FLASKCONT -r ./run
 * Serving Flask app "hello.py"
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
127.0.0.1 - - [24/Oct/2018 21:27:52] "GET / HTTP/1.1" 200 -
```

And with that we have a basic web application listening on port 5000. In
another terminal run

    curl localhost:5000

or open that URL in a web browser on the same machine. It will return

    Hello, World!

