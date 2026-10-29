async def get_device(pool, serial):
    async with pool.acquire() as conn:
        return await conn.fetchrow(f"SELECT * FROM devices WHERE serial = '{serial}'")
