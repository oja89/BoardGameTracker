# PWP SPRING 2023

# BoardGameTracker
# Group information
* Markus Oja, markus.oja@student.oulu.fi
* Riina Annunen, riina.annunen@student.oulu.fi

![BGTlogo](https://github.com/oja89/BoardGameTracker/blob/master/media/BGT.png)

## Info
BoardGameTracker is a game statistic tracker API.
It uses Python with Flask and SQLAlchemy.
Work is still in progress.

## Installation 

Prerequisites:
Python
pip

Using commandline: (on Windows)

Install virtualenv
```
pip install virtualenv
```

Create new virtualenv
(use name venv to have it .gitignored)
```
virtualenv venv
```

Activate venv
```
venv\Scripts\activate.bat
```

cd back to root
```
cd ..
cd ..
```

install required dependencies for your venv
```
pip install -r requirements.txt
```

run create_db.py to create your database under folder "instance"
```
python create_db.py
```

Use for example "DB Browser for SQLite" to open the db.

You can also create a shortcut on your desktop (on windows)
Use target `C:\Windows\System32\cmd.exe /K "[route_to_your_folder]\BoardGameTracker\venv\Scripts\activate.bat"`
And working directory `[route_to_your_folder]`






__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


