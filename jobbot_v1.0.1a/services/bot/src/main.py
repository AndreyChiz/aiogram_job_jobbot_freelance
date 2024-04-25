import asyncio
from aiohttp import web


async def handle(request):
    return web.Response(text="Hello, world!")


async def init_app():
    app = web.Application()
    app.router.add_get("/", handle)
    return app


async def main():
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    print("Server started at http://localhost:8000")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
