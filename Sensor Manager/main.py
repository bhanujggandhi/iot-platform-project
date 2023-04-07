# Om2m - http://192.168.137.185:5089/webpage

fetchAPI = "http://192.168.137.185:5089/~/in-cse/in-name/AE-DEV/Device-1/Data?rcn=4"
Headers = {'X-M2M-Origin': 'admin:admin',
           'Content-Type': 'application/json;ty=4'}


def SensorManager():
    """
    This function will be responsible for processing API requests received from the RqstManager and
    sending the appropriate response back to the RqstManager.

    For Processing API requests, the SensorManager will after Verification of the request, send the request to the
    SensorStream and sensor Stream will process the request and send the response back to the ReqstManager.
    """
    pass


def ReqstManager():
    """
    This function will be endpoint for all the API requests received from the client , it will redirect the request to the
    SensorManager for processing and will send the response back to the client.
    """
    pass


def SensorStream():
    """
    This function will be responsible for fetching the data from Om2m and sending the data to ReqstManager upon request from sensorManager.
    2 Modes of Fetching data from Om2m:
    1.TimeSeries Data
    2.RealTime Stream
    """
    pass


def Validator():
    """
    This function will be responsible for validating the Sensor metadata  from SensorDB and respond the correctness of Sensor metadata.
    """
    pass


def LogManager():
    """
    This function will be responsible for logging all the requests received from the client and the responses staus Codes sent back to the client.
    """
    pass
