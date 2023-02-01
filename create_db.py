from db import *

# create app context
ctx = app.app_context()
ctx.push()


db.create_all()
print("Db created")

# add a player
p = Players(name='Nick')

db.session.add(p)
db.session.commit()

print(f"Added player {p.name} as {p}")

# add a team
t = Teams(name='Foxes')

db.session.add(t)
db.session.commit()

print(f"Added team {t.name} as {t}")

# add a map
m = Maps(name='dust')

db.session.add(m)
db.session.commit()

print(f"Added map {m.name} as {m}")

# add a ruleset
r = Rulesets(name='competitive')

db.session.add(r)
db.session.commit()

print(f"Added ruleset {r.name} as {r}")

# add a game
g = Games(name='CS:GO')

db.session.add(g)
db.session.commit()

print(f"Added game {g.name} as {g}")

m1 = Matches(date="sorrythisisstring", turns=30)

db.session.add(m1)
db.session.commit()

print(f"Added match on date {m1.date} as {m1}")

pr = Player_results(points=23)

db.session.add(pr)
db.session.commit()

print(f"Added player score {pr.points} as {pr}")


tr = Team_results(points=56)

db.session.add(tr)
db.session.commit()

print(f"Added team score {tr.points} as {tr}")

# remove app context
ctx.pop()