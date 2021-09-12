#!/usr/bin/python

# Game ID and name not needed, search by UPC unless UPC not available
# game_name='Zelda II Link'

# Sample UPCs for testing
# Zelda II NES - upc = '045496630331'
# Dragon Warrior NES - upc = '045496630379'
# Boogerman SEGA - upc = '040421830183'
# Scaler Gamecube - upc = '710425245763'
# Doom 32X - upc = '010086845068'
# Metal Head 32X - upc = '010086845112'

# Need api_config.py file with token='apikey' set for this to work
import json
import api_config
import requests
import pprint
import datetime
from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model

def game_inc(upc, loc):
    increment_qty = Games.update({Games.qty: Games.qty + 1}).where((Games.upc == upc) & (Games.location == loc) & (Games.condition == cond))
    increment_qty.execute()

def get_remote_game_data(upc):
    # Sample output
    # {'console-name': 'Super Nintendo', 'id': '6910', 'loose-price': 32906, 'product-name': 'EarthBound', 'status': 'success'}
    resp = requests.get(api_url, params = {'t': api_config.token, 'upc': upc})
    return resp.json()

def game_create(game):
    print("Creating entry for new game")
    game = Games.create(**game)  
    game.save()
    return game.id

def db_get_game(upc, loc, cond):
    return Games.select().where((Games.upc == upc) & (Games.location == loc) & (Games.condition == cond))

def db_get_game_id(id):
    return Games.get_by_id(id)

db = SqliteDatabase('inventory.db')

class Games(Model):
    id = AutoField(primary_key=True)
    location = TextField()
    condition = TextField()
    vgpc_id = IntegerField()
    product_name = TextField()
    console_name = TextField()
    loose_price = IntegerField()
    qty = IntegerField()
    upc = IntegerField()
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db # This model uses the "people.db" database.

db.connect()
db.create_tables([Games])

api_url = 'https://www.pricecharting.com/api/product'

pp = pprint.PrettyPrinter(indent = 4)

cond = None # init location cond - example, cloose for loose, ccib for complete in box, cib for in box not complete, cnew for new
loc = None # init location var - example, b1 for box1, s3 for shelf 3
while True: # keep running until user types 'exit'
    print("Current settings: Location = {}, Condition = {}".format(loc,cond))
    answer = input("Enter Video Game UPC Code, Condition Code, Box Location Code, or 'exit' to exit: ") # get the UPC code from user

    if answer == "exit":
        break

    if answer == "CLOOSE" or answer == "CNEW" or answer == "CCIB" or answer == "CIB":
        cond = answer
        continue

    if answer.startswith('BOX') or answer.startswith('SHELF'): # if the answer starts with 'b' or 's', we are setting the location
        loc = answer
        continue

    if not loc or not cond: # make sure we have a condition and location set before scanning UPC codes
        print("Box location and condition must be set before scanning UPC codes!")
        continue
    
    game_id = None
    if db_get_game(answer, loc, cond): # if the UPC already exists in the DB table, let's increment the QTY
        print("Duplicate game and location, incrementing qty")
        game_inc(answer, loc)
        for row in db_get_game(answer, loc, cond):
            game_id = row.id
    else: # if 'answer' is not set to 'exit', let's get the game and store it
        print("Didn't find game")
        # pp.pprint(resp.headers)
        # pp.pprint(resp.json())
        
        r = get_remote_game_data(answer)
        # pp.pprint(r)
        
        id = game_create({
            'vgpc_id': r['id'],
            'location': loc,
            'condition': cond,
            'product_name': r['product-name'], 
            'console_name': r['console-name'],
            'loose_price': r['loose-price'],
            'upc': answer,
            'qty': 1
        })

        # pull it back out
        game_id = id
    
    pp.pprint(model_to_dict(db_get_game_id(game_id)))

db.close()