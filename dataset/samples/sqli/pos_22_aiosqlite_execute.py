import aiosqlite


async def add_note(db_path, owner, body):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(f"INSERT INTO notes (owner, body) VALUES ('{owner}', '{body}')")
        await db.commit()
