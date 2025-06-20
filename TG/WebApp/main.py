import os, aiosqlite
from fastapi import FastAPI

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..', 'Data', 'DataBase','shop.db'))

async def make_connection():
	if os.path.exists(db_path):
		return await aiosqlite.connect(db_path)
	else:
		print("No database found")
		return None

app = FastAPI()

@app.get("/")
async def root():
	return {"message": "Hello World"}

@app.get("/cart/{cart_id}")
async def cart(cart_id: int):
	conn = await make_connection()
	cursor = await conn.cursor()

	products = []
	await cursor.execute("""
		SELECT Products.name,
        CartItems.quantity
        FROM CartItems
        JOIN Products ON CartItems.product_id = Products.id
        WHERE CartItems.cart_id = ?
	    """, (cart_id,))
	data =  await cursor.fetchall()
	print(data)
	return {"data": data}