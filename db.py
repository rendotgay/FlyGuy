import math
import random
import sqlite3


def get_db():
    return sqlite3.connect('flyguy.db')

def create_table() -> None:
    print("creating table")
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gifs (
        user1 INTERGER NOT NULL,
        user2 INTERGER NOT NULL,
        url TEXT NOT NULL,
        UNIQUE(user1, user2, url)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS xp (
        user_id INTERGER PRIMARY KEY NOT NULL,
        xp INTEGER DEFAULT 0
    )''')
    db.commit()
    db.close()

def check_gif(user1: int, user2: int, url) -> bool:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT COUNT(*)
        FROM gifs
        WHERE (user1 = ? AND user2 = ? OR user1 = ? AND user2 = ?)
          AND url = ?;
        ''', (user1, user2, user2, user1, url))
        count = cursor.fetchone()[0]
        if count == 0: # if old_gifs table exists, also check that
            try:
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM old_gifs
                    WHERE (user1 = ? AND user2 = ? OR user1 = ? AND user2 = ?)
                      AND url = ?;
                    ''', (user1, user2, user2, user1, url))
                count = cursor.fetchone()[0]
                db.close()
                print("CHECKING GIF SUCCESSFUL")
                return count == 0
            except sqlite3.OperationalError:
                print("ERROR CHECKING GIF")
                return True
        else:
            return False
    except sqlite3.OperationalError:
        print("ERROR CHECKING GIF")
        db.close()
        create_table()
        return check_gif(user1, user2, url)

def insert_gif(user1: int, user2: int, url):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
        INSERT INTO gifs (user1, user2, url)
        VALUES (?, ?, ?)
        ''', (user1, user2, url))
        db.commit()
    except sqlite3.OperationalError as e:
        print(f"ERROR INSERTING GIF: {e}")
        create_table()
        insert_gif(user1, user2, url)

def increment_rarity(user_id: int, rarity: str) -> None:
    """Increment the specified rarity counter for a user by 1."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
        INSERT INTO rarities (user_id, ''' + rarity + ''')
        VALUES (?, 1)
        ON CONFLICT(user_id) DO UPDATE SET ''' + rarity + ''' = ''' + rarity + ''' + 1
        WHERE user_id = ?
        ''', (user_id, user_id))
        db.commit()
    except sqlite3.OperationalError:
        print("ERROR INCREMENTING RARITY. IS THIS EVEN STILL USED?")
        create_table()
        increment_rarity(user_id, rarity)


def increment_xp(user_id: int, roll: str, multiplier: float = 1.0) -> int:
    """Increment the XP counter for a user by the specified amount."""
    db = get_db()
    cursor = db.cursor()
    if roll == 'common':  # 65% - Common
        xp = random.randint(45, 55)
    elif roll == 'uncommon':  # 23% - Uncommon
        xp = random.randint(77, 94)
    elif roll == 'rare':  # 8% - Rare
        xp = random.randint(126, 154)
    elif roll == 'epic':  # 3% - Epic
        xp = random.randint(207, 253)
    elif roll == 'legendary':  # 0.8% - Legendary
        xp = random.randint(405, 495)
    elif roll == 'mythic':  # 0.1% - Mythic
        xp = random.randint(1125, 1375)
    elif roll == 'holy':  # Holy
        xp = random.randint(2000, 5000)
    else:
        xp = 0
        print("ROLL ERROR")
    xp *= multiplier
    xp = math.ceil(xp)
    print(f"XP earned: {xp}")
    try:
        cursor.execute('''
                       INSERT INTO xp (user_id, xp)
                       VALUES (?, ?)
                       ON CONFLICT(user_id) DO UPDATE SET xp = xp + ?
                       WHERE user_id = ?
                       ''', (user_id, xp, xp, user_id))
        db.commit()
        return xp
    except sqlite3.OperationalError:
        print("ERROR INCREMENTING XP")
        create_table()
        return increment_xp(user_id, roll)


def get_xp(user_id: int) -> int:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT xp
        FROM xp
        WHERE user_id = ?
        ''', (user_id,))
        xp = cursor.fetchone()[0]
        return xp
    except sqlite3.OperationalError:
        print("ERROR GETTING XP")
        create_table()
        return get_xp(user_id)
    except TypeError:
        return 0