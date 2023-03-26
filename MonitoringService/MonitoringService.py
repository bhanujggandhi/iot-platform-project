"""
MONITORING SERVICE:
    * Gets initalized with a config file describing:
        - The rules for determining threshold

    * Will monitor the levels of CPU and memory usage for each instance of the 
    node in the node manager. It will use the rules in the config file to inform
    the node manager in case there is need of upscaling and downscaling.

    * Get the health status of all platform modules by hitting their healthcheck
    API.

    * Get the metrics of all services from the response time logs created by API Manager

    Assumes:
    * Node Manager is always up
    * API Manager is up when traffic data is asked
"""
import requests
import json


def getServiceInfo(filePath: str) -> dict:
    """get the service info from the Bootstrap Module"""
    # For now, we will get the service info from dummy service info file
    with open(filePath, "r") as f:
        response = json.load(f)

    return response


def getHealthStatus(IP: str, PORT: str) -> bool:
    api_url = f"http://{IP}:{PORT}/healthcheck"
    # get the response from the module at IP:PORT
    try:
        response = requests.get(api_url)
        # print(response.json())
        status = response.json()["status"]
    except Exception as e:
        # print(e)
        # refused to connect => no response
        status = False

    return status


def healthCheck(service_info: dict) -> None:
    """Iterate through the global list containing the IP:PORT of
    each service and get the health status of each service"""

    for service_name, socket_address in service_info.items():
        IP = socket_address["IP"]
        PORT = socket_address["PORT"]
        status = getHealthStatus(IP, PORT)

        if status == False:
            # the service is down
            print(f"{service_name}: [DOWN]")
            # contact someone to try restart the service
            # if not then run a new instance
            report = {
                "serviceName": service_name,
                "status": False,
            }
            headers = {"Content-Type": "application/json"}

            # get the IP and PORT of NodeManager
            socket_address = service_info["NodeManager"]
            IP = socket_address["IP"]
            PORT = socket_address["PORT"]

            api_url = f"http://{IP}:{PORT}/contact"
            response = requests.post(api_url, json=report)
            print(response.json())
        else:
            # the service is up
            print(f"{service_name}: [UP]")


def getTrafficLogs(service_info) -> dict:
    """Get the traffic logs from the API Manager module"""

    # get the IP and PORT of APIManager
    try:
        socket_address = service_info["APIManager"]
        IP = socket_address["IP"]
        PORT = socket_address["PORT"]
    except Exception as e:
        print(f"{e} is not in list of services")
        return dict()

    api_url = f"http://{IP}:{PORT}/traffic_logs"
    # get the response from the module at IP:PORT
    try:
        response = requests.get(api_url)
        return response

    except Exception as e:
        print(e)
        return dict()


def extractQoSValues(traffic_logs: dict) -> None:
    for microservice_name, logs in traffic_logs.items():
        requests = logs["requests"]
        responses = logs["responses"]

        total = min(len(requests), len(responses))

        response_times = []

        for query in range(total):
            response_times.append(responses[query] - requests[query])

        print(f"Reponse Time for {microservice_name}: ")
        print(response_times)


if __name__ == "__main__":
    service_info = getServiceInfo("./dummyBoostrapResponse.json")
    healthCheck(service_info)
    # traffic_logs = getTrafficLogs(service_info)
    with open("./dummyTrafficLogs.json") as f:
        traffic_logs = json.load(f)

    extractQoSValues(traffic_logs)
