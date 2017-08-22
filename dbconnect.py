import MySQLdb


def connInit():
    conn = MySQLdb.connect("your server", "your name", "your pwd", "datasheet name")
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    return conn,cursor
