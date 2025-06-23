import os, aiosqlite
from fastapi import APIRouter, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

router = APIRouter(
    prefix='/admin',
    tags=['admins']
)

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..', 'Data', 'DataBase','shop.db'))

async def make_connection():
	if os.path.exists(db_path):
		return await aiosqlite.connect(db_path)
	else:
		print("No database found")
		return None


static_dir = os.path.join(os.path.dirname(__file__), "src")
router.mount("/static", StaticFiles(directory=static_dir), name="static")

@router.get('/', response_class=HTMLResponse)
def admin_root():
    html_path = os.path.join(static_dir, "admin.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, media_type="text/html")

@router.post('/add_admin')
async def add_admin(data: dict):
    commands = 'new_entry,modify_entry,delete_entry'

    conn = await make_connection()
    cursor = await conn.cursor()

    await cursor.execute('SELECT user_id FROM Users Where username = ?', (data['username'],))
    id = await cursor.fetchone()
    await cursor.execute('''
    INSERT INTO admins (user_id, commands)
    VALUES (?, ?)
    ''', (id[0], commands))
    await conn.commit()
    await conn.close()
    return 0

@router.post('/delete_admin')
async def delete_admin(data: dict):
    print(data)
    conn = await make_connection()
    cursor = await conn.cursor()
    name = data['username']
    try:
        await cursor.execute(f'''
        DELETE FROM admins
        WHERE user_id IN (
        SELECT user_id 
        FROM Users 
        WHERE username = ?)
        ''', (name,))
        await conn.commit()
        await conn.close()
        return 0
    except aiosqlite.Error as e:
        print(f"DB error: {e}")
        await conn.close()
        return 1


@router.post('/new_entry')
async def new_entry(data: dict):
    print(data)

@router.post('/new_entry/Products')
async def new_entry_products(
    request: Request,
    name: str = Form(None),
    details: str = Form(None),
    speed: str = Form(None),
    capacity: str = Form(None),
    min_temp: str = Form(None),
    max_temp: str = Form(None),
    type: str = Form(None),
    price: str = Form(None),
    image: UploadFile = File(None)
):
    print("Endpoint called")  # Debug: see if function is called
    form = await request.form()
    print("Form data:", dict(form))
    conn = await make_connection()
    cursor = await conn.cursor()

    image_blob = None
    if image:
        image_blob = await image.read()

    try:
        await cursor.execute('''
            INSERT INTO Products 
            (image, name, details, speed, capacity, min_temp, max_temp, type, price)
            VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (image_blob,
              name,
              details,
              float(speed),
              int(capacity),
              float(min_temp) if min_temp else 0,
              float(max_temp) if max_temp else 0,
              type,
              float(price)))
        await conn.commit()
        await conn.close()
    except aiosqlite.Error as e:
        print(f'DB Error: {e}')
        await conn.close()


@router.post('/modify_entry')
def modify_entry(data: dict):
    print(data)
    return 0

@router.post('/delete_entry')
def delete_entry(data: dict):
    print(data)
    id = data['entryid']
    return 0

@router.get('/get_users')
async def get_users():
    conn = await make_connection()
    cursor = await conn.cursor()
    users = []
    await cursor.execute('''
    SELECT u.username
    FROM Users u
    WHERE NOT EXISTS (
    SELECT user_id
    FROM admins a
    WHERE a.user_id = u.user_id)
    ''')
    data = await cursor.fetchall()
    for row in data:
        users.append(row[0])
    await conn.close()
    return {'users': users}

@router.get('/get_admins')
async def get_admins():
    conn = await make_connection()
    cursor = await conn.cursor()
    admins = []
    await cursor.execute('''
    SELECT u.username
    FROM Users u
    INNER JOIN admins a ON u.user_id = a.user_id;
    ''')
    data = await cursor.fetchall()
    for row in data:
        admins.append(row[0])
    await conn.close()
    return {'admins': admins}
