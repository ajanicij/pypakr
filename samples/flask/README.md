Create image:

pypakr create-image -s FLASK.tar -i IMAGE.tar

Create container:

pypakr create-container -i IMAGE.tar -c CONT

Run:

pypakr run -c CONT -r ./run
