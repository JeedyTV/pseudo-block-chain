import json
import time
from requests import get
import argparse

parser = argparse.ArgumentParser("to perform tests")

parser.add_argument("--throughput", type=str, 
                    help="Starts the mining procedure.")
parser.add_argument("--attack", type=str, 
                    help="Starts the mining procedure.")

arguments, _ = parser.parse_known_args()


try:
    if arguments.throughput:
        i = 0
        while i < 200 :
            print(f"add {i} Transaction")
            get("http://localhost:5000/testing", data=json.dumps({"key":"key", "value": i}))
            time.sleep(1)
            i += 1
    if arguments.attack:
        i = 0
        while True :
            print(f"add {i} Transaction")
            get("http://localhost:5000/testing", data=json.dumps({"key":"key", "value": i}))
            get("http://localhost:5001/testing", data=json.dumps({"key":"key", "value": i}))
            time.sleep(1)
            i += 1
except Exception:
    exit(0)