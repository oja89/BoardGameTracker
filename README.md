# PWP SPRING 2023

# BoardGameTracker
# Group information
* Markus Oja, markus.oja@student.oulu.fi
* Riina Annunen, riina.annunen@student.oulu.fi

![BGTlogo](https://github.com/oja89/BoardGameTracker/blob/master/media/BGT.png)

## Info
BoardGameTracker is an API for tracking game results.

It uses Python with Flask and SQLAlchemy.

Work is still in progress.

It uses SQLite database.

There is a sample database called example_db.db provided.

## Installation 

### Prerequisites:
-Python

-pip

-pytest (if testing)
-pytest-cov

(requirements.txt is used for installing dependencies using pip)

(Guide is for Windows)

Using command line:

Install virtualenv
```
pip install virtualenv
```

Create new virtualenv
(use name venv to have it .gitignored)
```
virtualenv venv
```

Activate the virtual environment
```
venv\Scripts\activate.bat
```

Install the project in editable mode:
```
pip install -e .
```

Set Flask variables:
```
set FLASK_APP=boardgametracker
set FLASK_DEBUG=true
```

Initialize database:
```
flask init-db
```

Populate database with example data:
```
flask testgen
```

Testing with pytest:
```
pytest --cov-report term-missing --cov=boardgametracker
```

Testing with pylint:
```
pylint ./boardgametracker
```

Starting flask service:
```
flask run
```

(Deploying on pythonanywhere:)
```
export FLASK_APP=boardgametracker
flask init-db
flask testgen
```

Also change the URL in pyscript_code from 127.0.0.1:5000 to what is used...

The PyScript site (GUI) can be found at /pyscript
For example oja89.pythonanywhere.com/pyscript



## Shortcut for venv

You can also create a shortcut on your desktop (on Windows) to open the venv directly.

Use target:

`C:\Windows\System32\cmd.exe /K "[route_to_your_folder]\BoardGameTracker\venv\Scripts\activate.bat"`

And working directory 

`[route_to_your_folder]`






__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


