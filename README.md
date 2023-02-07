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

## Installation 

### Prerequisites:
-Python
-pip
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

cd back to root
```
cd ..
cd ..
```

Install required dependencies for your venv:
```
pip install -r requirements.txt
```

Run create_db.py to create and populate your database:
```
python create_db.py
```

Database (maindata.db) is created inside folder "instance".

Use for example "DB Browser for SQLite" to open the db.

This db needs to be deleted and recreated (for example using create_db.py) if models in db.py are modified!

## Shortcut for venv

You can also create a shortcut on your desktop (on Windows) to open the venv directly.
Use target 

`C:\Windows\System32\cmd.exe /K "[route_to_your_folder]\BoardGameTracker\venv\Scripts\activate.bat"`

And working directory 

`[route_to_your_folder]`






__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


