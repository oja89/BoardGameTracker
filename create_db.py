from db import *

# create app context
ctx = app.app_context()
ctx.push()


db.create_all()
print("Db created")

### Basic resources

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



### Resources with relationships

## Game, rules, maps

#add a game
g = Games(name='CS:GO')
db.session.add(g)
db.session.commit()
print(f"Added game {g.name} as {g}")

# add map for the game
m = Maps(
    name='dust', 
    game_id=g.id
    )
db.session.add(m)
db.session.commit()
print(f"Added map {m.name} as {m} for game {g.name} {g}")

# add ruleset for the game
r = Rulesets(
    name='competitive', 
    game_id=g.id
    )
db.session.add(r)
db.session.commit()

print(f"Added ruleset {r.name} as {r} for game {g.name} {g}")


### Match
# match info, use game, map, ruleset
m1 = Matches(
    date="sorrythisisstring", 
    turns=30,
    game_id=g.id,
    map_id=m.id,
    ruleset_id=r.id
    )

db.session.add(m1)
db.session.commit()

print(f"Added match on date {m1.date} as {m1}, with {g}, {m}, {r}")



# team results, use match, team
tr = Team_results(
    points=56,
    order=2,
    match_id=m1.id,
    team_id=t.id
    )

db.session.add(tr)
db.session.commit()

print(f"Added team score {tr.points} as {tr} for match {m1}")

# player results, use match, player, team
pr = Player_results(
    points=23,
    match_id=m1.id,
    team_id=t.id,
    player_id=p.id
    )

db.session.add(pr)
db.session.commit()

print(f"Added player score {pr.points} as {pr}")







db.session.commit()








# remove app context
ctx.pop()