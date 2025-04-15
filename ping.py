import requests
import time
saite = "https://martinsvagins.id.lv"
while True:
    if requests.get(saite):
        print("pieslēdzies")
    time.sleep(300)