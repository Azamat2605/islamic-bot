from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n.core import I18n
from aiohttp import web

from bot.core.config import DEFAULT_LOCALE, I18N_DOMAIN, LOCALES_DIR, settings

app = web.Application()

token = settings.BOT_TOKEN

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

storage = MemoryStorage()

dp = Dispatcher(storage=storage)

i18n: I18n = I18n(path=LOCALES_DIR, default_locale=DEFAULT_LOCALE, domain=I18N_DOMAIN)

DEBUG = settings.DEBUG

# Redis stub for modules that require redis_client
class RedisStub:
    """Stub for redis client to avoid connection errors when Redis is not available."""
    async def get(self, key):
        return None
    async def set(self, key, value, ex=None):
        pass
    async def delete(self, key):
        pass
    async def pipeline(self, transaction=False):
        class PipelineStub:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
            async def set(self, key, value):
                pass
            async def expire(self, key, ttl):
                pass
            async def execute(self):
                pass
        return PipelineStub()
    async def close(self):
        pass

redis_client = RedisStub()
