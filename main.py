import asyncio

from dotenv import load_dotenv
from queries import example_test

load_dotenv()
asyncio.run(example_test.example())