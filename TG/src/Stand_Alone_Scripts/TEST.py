import sqlite3
path = "C:/Users/SunPixel/Desktop/Programming/VSC/Bots/TG/Data/DataBase/shop.db"
path1 = "C:/Users/SunPixel/Desktop/Programming/VSC/Bots/TG/Data/DataBase/Standard.png"
conn = sqlite3.connect(path)
cursor = conn.cursor()

with open(path1, 'rb') as file:
    image = file.read()
    print('All good')


cursor.execute('''
insert into Products (image, name, price)
values (?, ?, ?)
''', (image, 'Abebebe', 123.2))
conn.commit()