from tortoise import Tortoise, run_async

from api import settings


async def migrate():
    await Tortoise.init(
        db_url=settings.DATABASE_SETTING['HOST'],
        modules={'models': [settings.DATABASE_SETTING['MODELS']]}
    )
    await Tortoise.generate_schemas()

    print("Success migration!!")


if __name__ == '__main__':
    run_async(migrate())
