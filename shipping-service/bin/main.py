import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
count = 0


async def main():
    global count
    while True:
        logger.info(f"Current: {count}")
        count += 1
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
