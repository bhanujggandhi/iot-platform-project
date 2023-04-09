import requests
from apscheduler.schedulers.blocking import BlockingScheduler


def make_api_request():
    url = "http://127.0.0.1:8000/api"
    response = requests.get(url)
    if response.status_code == 200:
        response_json = response.json()  # Deserialize the JSON response content
        print("API hit successful")
        print(response_json)  # Print the response as JSON
    else:
        print("Error hitting API")

hr = 23
min = 56
scheduler = BlockingScheduler()
scheduler.add_job(make_api_request, 'cron', hour=hr, minute=min)
scheduler.start()
