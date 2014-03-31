
Installation
============

Steps to setup this example::

    $ cd tic-tac-toe
    $ python bootstrap.py
    $ ./bin/buildout
    $ ./bin/django syncdb
    $ ./bin/django runserver_socketio

If you encounter an error running python bootstrap.py
run this command::
	
    $ python bootstrap.py -d -v 2.1.1
	
If you encounter an error with ./bin/buildout move setup.py to same directory django-tictactoe is in. 

