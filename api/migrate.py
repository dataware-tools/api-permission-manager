from tortoise import Tortoise, run_async

from api import settings


async def migrate():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print("Success migration!!")


if __name__ == '__main__':
    run_async(migrate())
