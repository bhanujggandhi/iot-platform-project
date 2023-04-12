import json 
import requests

def service_req(service_name, args):
    print()
    print("Calling " + service_name)

    f = open("../exposed_urls.json")
    eud = json.load(f)
    f.close()

    url = eud[service_name]['url']
    input = eud[service_name]['input']

    params = {}
    
    for i, arg in enumerate(args):
        params[input[i]['name']] = arg

    # print(params)

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print(service_name + " executed successfully..!!")
        print("Finishing " + service_name)
        return response.json()
    
    else:
        print(service_name + " failed..!!")
        return {"error" : True}
    