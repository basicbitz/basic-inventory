#!/usr/bin/python

# Need api_config.py file with 'token' set for this to work
import json
import api_config
import requests
import pprint
import sqlite3

api_url = 'https://www.pricecharting.com/api/product'
upc='710425245763'

# Game ID and name not needed, search by UPC unless UPC not available
game_id='6910'
game_name='Zelda II Link'


# Sample UPCS
# Zelda II NES
# upc='045496630331'
# Dragon Warrior NES
# upc='045496630379'
# Boogerman SEGA
# upc='040421830183'
# Scaler Gamecube

# Create the DB
conn = sqlite3.connect('inventory.db')
print("Opened database successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS GAMES
         (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         VGPC_ID        INT     NOT NULL,
         PRODUCT_NAME   TEXT    NOT NULL,
         CONSOLE_NAME   TEXT    NOT NULL,
         LOOSE_PRICE    INT     NOT NULL,
         QTY            INT     NOT NULL,
         UPC            INT);''')

# TODO: Add UPC TABLE (write UPC to both tables)
# TODO: Add readline/pause/scanner capability
# TODO: Allow adding game based on name with confirmation/approval (verify proper game found on text search before saving)
# TODO: Manage game quantity (allow increment QTY if game entry already exists in GAMES)
# TODO: Allow decrement/removal if games are sold
# TODO: look at sqlalchemy or peewee

# Sample output
# {'console-name': 'Super Nintendo', 'id': '6910', 'loose-price': 32906, 'product-name': 'EarthBound', 'status': 'success'}

# resp = requests.get(api_url, params={'t': api_config.token, 'id': game_id})
# resp = requests.get(api_url, params={'t': api_config.token, 'q': game_name})

resp = requests.get(api_url, params={'t': api_config.token, 'upc': upc})
pp = pprint.PrettyPrinter(indent=4) 
# pp.pprint(resp.headers)
# pp.pprint(resp.json())

game={} # initialize the game dict
game['vgpc_id'] = resp.json()['id'] # Video Game Price Charting game ID
game['product_name'] = resp.json()['product-name'] # product name
game['console_name'] = resp.json()['console-name'] # name of console
game['loose_price'] = resp.json()['loose-price'] # loose price of game
qty=1 # this needs to be actual QTY (if new entry, set to 1 - increment each additional)

pp.pprint(game)

# for x in range(5000):
#     conn.execute(f"INSERT INTO GAMES (VGPC_ID,PRODUCT_NAME,CONSOLE_NAME,LOOSE_PRICE,QTY,UPC) \
#         VALUES ({game['vgpc_id']}, '{game['product_name']}', '{game['console_name']}', {game['loose_price']}, {qty}, {upc})" );
conn.execute(f"INSERT INTO GAMES (VGPC_ID,PRODUCT_NAME,CONSOLE_NAME,LOOSE_PRICE,QTY,UPC) \
    VALUES ({game['vgpc_id']}, '{game['product_name']}', '{game['console_name']}', {game['loose_price']}, {qty}, {upc})" );
conn.commit()

conn.close()