from db import db, app, Players, Teams, Maps

# create app context
ctx = app.app_context()
ctx.push()


db.create_all()

print("Db created")


# remove app context
ctx.pop()