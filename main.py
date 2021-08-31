#!/usr/bin/python

# Need api_config.py file with 'token' set
import json
import api_config
import requests
import pprint
import sqlite3

api_url = 'https://www.pricecharting.com/api/product'
game_id='6910'
game_name='Zelda II Link'
# Zelda II NES
# upc='045496630331'
# Dragon Warrior NES
# upc='045496630379'
# Boogerman SEGA
# upc='040421830183'
# Scaler Gamecube
upc='710425245763'

# Create the DB
conn = sqlite3.connect('inventory.db')
print("Opened database successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS GAMES
         (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         VGPC_ID        INT     NOT NULL,
         PRODUCT_NAME   TEXT    NOT NULL,
         CONSOLE_NAME   TEXT    NOT NULL,
         LOOSE_PRICE    INT     NOT NULL);''')



# Sample output
# {'console-name': 'Super Nintendo', 'id': '6910', 'loose-price': 32906, 'product-name': 'EarthBound', 'status': 'success'}

# resp = requests.get(api_url, params={'t': api_config.token, 'id': game_id})
# resp = requests.get(api_url, params={'t': api_config.token, 'q': game_name})

resp = requests.get(api_url, params={'t': api_config.token, 'upc': upc})
pp = pprint.PrettyPrinter(indent=4) 
# pp.pprint(resp.headers)
# pp.pprint(resp.json())

game={}
game['vgpc_id'] = resp.json()['id']
game['product_name'] = resp.json()['product-name']
game['console_name'] = resp.json()['console-name']
game['loose_price'] = resp.json()['loose-price']

pp.pprint(game)

# look at sqlalchemy or peewee

conn.execute(f"INSERT INTO GAMES (VGPC_ID,PRODUCT_NAME,CONSOLE_NAME,LOOSE_PRICE) \
      VALUES ({game['vgpc_id']}, '{game['product_name']}', '{game['console_name']}', {game['loose_price']})" );
conn.commit()

conn.close()