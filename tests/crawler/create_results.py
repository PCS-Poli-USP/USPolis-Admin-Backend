from common.crawler import JupiterCrawler
import unittest
import json

def run(input_strings, output_file):
    results = {}

    for input_string in input_strings:
        try:
            results[input_string] = JupiterCrawler.crawl_subject_static(input_string)
        except Exception as e:
            print(f"error on: {input_string}")
            raise e

    with open(output_file, "w") as f:
        f.write(json.dumps(results, indent=4, ensure_ascii=False))

if(__name__ == "__main__"):
    input_file_path = "./crawler_test_cases"
    with open(input_file_path, 'r') as f:
        input_strings = [line.strip() for line in f.readlines()]

    output_file_path = 'new_test_results.json'
    run(input_strings, output_file_path)