import asyncio
import json
import pickle

from server.services.jupiter_crawler.crawler import JupiterCrawler


async def run() -> None:
    results = {}

    contents_file_path = "tests/services/jupiter_crawler/html_contents"
    results_file_path = "tests/services/jupiter_crawler/new_results.json"

    with open(contents_file_path, "rb") as file:
        contents_dict: dict[str, bytes] = pickle.load(file)

        for subject_code, content in contents_dict.items():
            result = await JupiterCrawler.crawl_subject_static(subject_code, content)
            results[subject_code] = json.loads(result.model_dump_json())

    with open(results_file_path, "w") as f:
        f.write(json.dumps(results, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(run())
