import sys
import logging

from aiohttp import web

from aio_connect.types import HookType
from config_reader import config
from aio_connect.fsm.storage.memory import MemoryStorage
from aio_connect import Bot, Dispatcher
from aio_connect.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from filters.sent_by_user import SentByUserFilter
from filters.slowpoke_middleware import SlowpokeMiddleware

SERVER_API = config.SERVER_API

# host
BASE_WEBHOOK_URL = config.BASE_WEBHOOK_URL
WEBHOOK_PATH = config.WEBHOOK_PATH

# listen
WEB_SERVER_HOST = config.WEB_SERVER_HOST
WEB_SERVER_PORT = config.WEB_SERVER_PORT

# line
LINE_ID = config.LINE_ID

bot = Bot(
    api_login=config.API_LOGIN.get_secret_value(),
    api_password=config.API_PASSSWORD.get_secret_value(),
    line_id=LINE_ID,
    base=SERVER_API
)


async def on_startup():
    from handlers.applications_function import set_application_info_lists
    await bot.set_hook(type=HookType.BOT, id=LINE_ID, url=BASE_WEBHOOK_URL + WEBHOOK_PATH + LINE_ID)
    await set_application_info_lists()


async def on_shutdown():
    print("Завершение программы ...")


def main() -> None:
    from handlers import (
        navigation_menu, navigation_function, register_of_application, applications_function, response_to
    )
    from aio_connect.fsm.storage.memory import SimpleEventIsolation
    dp = Dispatcher(storage=MemoryStorage(), events_isolation=SimpleEventIsolation())
    dp.include_routers(
        navigation_menu.router,
        navigation_function.router,

        register_of_application.router,
        applications_function.router,

        response_to.router,
    )
    navigation_menu.router.line.middleware(SlowpokeMiddleware(sleep_sec=0))
    navigation_menu.router.line.filter(SentByUserFilter())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH + LINE_ID)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    sys.exit()


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.error("Exit")
