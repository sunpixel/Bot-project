import os, aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..', 'Data', 'DataBase','shop.db'))

async def make_connection():
	if os.path.exists(db_path):
		return await aiosqlite.connect(db_path)
	else:
		print("No database found")
		return None

app = FastAPI()


static_dir = os.path.join(os.path.dirname(__file__), "src")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/{user_id}", response_class=HTMLResponse)
async def root(user_id: int):
    conn = await make_connection()
    cursor = await conn.cursor()
    await cursor.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,))
    data = await cursor.fetchone()
    await cursor.close()
    await conn.close()
    cart_id = data[0] if data else -1

    html_path = os.path.join(static_dir, "main.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    # Inject cart_id as a JS variable
    html_content = html_content.replace(
        "</head>",
        f"<script>window.CART_ID = {cart_id};</script></head>"
    )
    return HTMLResponse(content=html_content, media_type="text/html")

@app.get("/cart/{cart_id}")
async def cart(cart_id: int):
    conn = await make_connection()
    cursor = await conn.cursor()
    await cursor.execute("""
        SELECT Products.name,
               CartItems.quantity,
               Products.id
        FROM CartItems
        JOIN Products ON CartItems.product_id = Products.id
        WHERE CartItems.cart_id = ?
    """, (cart_id,))
    data = await cursor.fetchall()
    await cursor.close()
    await conn.close()
    return {"data": data}


@app.post('/cart/{cart_id}/update')
async def update_cart(cart_id: int, request: Request):
    data = await request.json()
    item_id = data.get("product_id")
    item_qty = data.get("quantity")

    conn = await make_connection()
    cursor = await conn.cursor()
    await cursor.execute("""
        UPDATE CartItems
        SET quantity = ?
        WHERE cart_id = ? AND product_id = ?
    """, (item_qty, cart_id, item_id))
    await conn.commit()
    await cursor.close()
    await conn.close()
    return {"status": "success"}

@app.delete('/cart/${cartId}/item/${productId}')
async def delete_item(cart_id: int, product_id: int):
	conn = await make_connection()
	cursor = await conn.cursor()
	await cursor.execute("""
		DELETE FROM CartItems
		WHERE cart_id = ? AND product_id = ?
	""", (cart_id, product_id))
	await conn.commit()
	await cursor.close()
	await conn.close()


@app.post('/buy/{cart_id}')
async def buy_cart(cart_id = -1):
	if cart_id != -1:
		conn = await make_connection()
		cursor = await conn.cursor()
		await cursor.execute("""
                             SELECT Products.name,
                                    CartItems.quantity,
	                                Products.price
                             FROM CartItems
                                      JOIN Products ON CartItems.product_id = Products.id
                             WHERE CartItems.cart_id = ?
		                     """, (cart_id,))
		data = await cursor.fetchall()
		total = lambda x: sum(item[1] * item[2] for item in x)
		total_price = total(data)
		return {"total": total_price}

@app.post('/buy')
def buy_products(product: dict):
	return {'Data': product}


