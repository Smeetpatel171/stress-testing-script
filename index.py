import asyncio
import aiohttp

API_URL = "https://yaapp-oct24-demo-371492433575.us-central1.run.app"  # Replace with your API endpoint

async def fetch(session, url, index):
    async with session.get(url) as response:
        data = await response.text()
        print(f"Response {index}: {data}")
        return data

async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(50):  # 50 concurrent calls
            tasks.append(fetch(session, API_URL, i))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
