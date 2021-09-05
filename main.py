#!/usr/bin/python

# Need api_config.py file with 'token' set for this to work
import json
import api_config
import requests
import pprint
import datetime
from peewee import *

db = SqliteDatabase('inventory.db')

class Games(Model):
    id = AutoField(primary_key=True)
    # location = TextField()
    vgpc_id = IntegerField()
    product_name = TextField()
    console_name = TextField()
    loose_price = IntegerField()
    qty = IntegerField()
    upc = IntegerField(unique=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db # This model uses the "people.db" database.

db.connect()
db.create_tables([Games])

api_url = 'https://www.pricecharting.com/api/product'

# Game ID and name not needed, search by UPC unless UPC not available
# game_id='6910'
# game_name='Zelda II Link'

# Create the DB
# conn = sqlite3.connect('inventory.db')
# print("Opened database successfully")
# conn.execute('''CREATE TABLE IF NOT EXISTS GAMES
#          (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#          VGPC_ID        INT     NOT NULL,
#          PRODUCT_NAME   TEXT    NOT NULL,
#          CONSOLE_NAME   TEXT    NOT NULL,
#          LOOSE_PRICE    INT     NOT NULL,
#          QTY            INT     NOT NULL,
#          UPC            INT);''')

# TODO: Add UPC TABLE (write UPC to both tables)
# TODO: Allow adding game based on name with confirmation/approval (verify proper game found on text search before saving)
# TODO: Allow decrement/removal if games are sold
# TODO: Add column for box label
# TODO: Handle `{'error-message': 'No such product', 'status': 'error'}` when UPC scanned is not a valid game UPC

# Sample UPCS
# Zelda II NES
# upc='045496630331'
# Dragon Warrior NES
# upc='045496630379'
# Boogerman SEGA
# upc='040421830183'
# Scaler Gamecube
# upc='710425245763'
# Doom 32X
# upc='010086845068'
# Metal Head 32X
# upc='010086845112'

upc = 0 # init upc var
while upc != "exit": # keep running until user types 'exit'
    upc = input("Enter Video Game UPC Code: ") # get the UPC code from user

    query = Games.select().where(Games.upc == upc) # Check if the UPC already exists in the DB

    # Sample output
    # {'console-name': 'Super Nintendo', 'id': '6910', 'loose-price': 32906, 'product-name': 'EarthBound', 'status': 'success'}

    duplicate = bool(query) # is False if UPC does not exist in DB table, is True if UPC does already exist in DB table

    if duplicate == True: # if the UPC already exists in the DB table, let's increment the QTY
        increment_qty = Games.update({Games.qty: Games.qty + 1}).where(Games.upc == upc)
        increment_qty.execute()
        
    if (duplicate == False) and (upc != "exit"): # if 'upc' is not set to 'exit', let's get the game info and store it
        resp = requests.get(api_url, params = {'t': api_config.token, 'upc': upc})
        pp = pprint.PrettyPrinter(indent = 4) 
        # pp.pprint(resp.headers)
        # pp.pprint(resp.json())
        
        r = resp.json()
        pp.pprint(r)

        game = Games.create(vgpc_id = r['id'],
                            product_name = r['product-name'], 
                            console_name = r['console-name'],
                            loose_price = r['loose-price'],
                            upc = upc,
                            qty = 1)
        
        game.save()

db.close()