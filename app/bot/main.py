import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from app.core.config import settings
from handlers_commands import router as commands_router
from handlers_messages import router as messages_router


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(token=settings.TELEGRAM_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(commands_router)
    dp.include_router(messages_router)

    try:
        if not settings.WEBHOOK_DOMAIN:
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types()
            )
        else:
            aiohttp_logger = logging.getLogger('aiohttp.access')
            aiohttp_logger.setLevel(logging.DEBUG)

            await bot.set_webhook(
                url=settings.WEBHOOK_DOMAIN + settings.WEBHOOK_PATH,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )

            app = web.Application()
            SimpleRequestHandler(
                dispatcher=dp, bot=bot
            ).register(app, path=settings.WEBHOOK_PATH)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner,
                               host=settings.APP_HOST,
                               port=settings.APP_PORT
                               )
            await site.start()
            await asyncio.Event().wait()
    except RuntimeError:
        pass
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
