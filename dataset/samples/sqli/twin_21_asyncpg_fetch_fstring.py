async def get_device(pool, serial):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM devices WHERE serial = $1", serial)
