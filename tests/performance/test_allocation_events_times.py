from time import time
import requests

MAX_TRIES = 10


def allocation_events_benchmark() -> None:
    url = "http://localhost:8000/allocations/events?start=2025-11-10&end=2025-11-16"

    start = time()
    for i in range(MAX_TRIES):
        curr_start_time = time()
        requests.get(url)
        curr_end_time = time()
        print(f"Current delta {i + 1} = {curr_end_time - curr_start_time}")
    end = time()

    print("Total time: ", end - start)


if __name__ == "__main__":
    allocation_events_benchmark()
