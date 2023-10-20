import json
import sys
from datetime import datetime
from typing import List

import numpy as np
from bson.objectid import ObjectId
from decouple import config
from fastapi import APIRouter, Query, params
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from utils.logger_utils import Logger
from utils.Messenger import Consume, Produce
from utils.remotecalls import *

sys.path.append("..")


TOPIC = "topic_analytics"
TOPIC_HEALTH = "topic_analytics_health"
SERVICE_NAME = "Analytics Module"
produce = Produce()
consume = Consume(TOPIC)

logger = Logger()  # Instantiate logger


# Initialize MongoDB client
mongokey = config("mongoKey")
client = MongoClient(mongokey)

# Initialize FastAPI app
router = APIRouter()

# Define MongoDB collections
platform_db = client["platform"]
user_collection = platform_db.User
app_collection = platform_db.App
sensor_db = client["SensorDB"]


# checks if the developer exists or not
def is_valid_developer(developer_id):
    try:
        # check if the user exists in the user collection
        user = user_collection.find_one({"_id": ObjectId(developer_id)})
        if user:
            return True
        else:
            return False
    except Exception as e:
        # handle any exceptions that may occur
        logger.log(
            service_name=SERVICE_NAME, level=3, msg=f"Error checking developer: {e}"
        )
        print(f"Error checking developer: {e}")
        return False


# checks if this app belongs to the developer or not
def is_valid_app(developer_id, app_id):
    try:
        # check if the app exists in the app collection for the given developer
        query = {"user": ObjectId(developer_id)}
        results = app_collection.find(query)
        app_ids = [str(result["_id"]) for result in results]
        if app_id in app_ids:
            return True
        else:
            return False
    except Exception as e:
        # handle any exceptions that may occur
        logger.log(service_name=SERVICE_NAME, level=3, msg=f"Error checking app: {e}")
        print(f"Error checking app:")
        return False


def format_timestamps(timestamps: List[str]) -> List[str]:
    try:
        formatted_timestamps = []
        for timestamp in timestamps:
            dt = datetime.fromisoformat(timestamp)
            formatted_timestamps.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
        return formatted_timestamps
    except Exception as e:
        logger.log(
            service_name=SERVICE_NAME,
            level=3,
            msg=f"Error: {e}. in 'format_timestamps' method",
        )
        print(f"some thing went wrong while timestamps formating")
        return None


def generate_datasets(data_list):
    datasets = []
    colors = [
        "rgba(255, 99, 132, 0.6)",
        "rgba(54, 162, 235, 0.6)",
        "rgba(255, 206, 86, 0.6)",
        "rgba(75, 192, 192, 0.6)",
        "rgba(153, 102, 255, 0.6)",
        "rgba(255, 159, 64, 0.6)",
    ]
    border_colors = [
        "rgba(255, 99, 132, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(255, 206, 86, 1)",
        "rgba(75, 192, 192, 1)",
        "rgba(153, 102, 255, 1)",
        "rgba(255, 159, 64, 1)",
    ]
    for i, data in enumerate(data_list):
        dataset = {
            "label": f"Sensor {i+1}",
            "data": data,
            "backgroundColor": colors[i % len(colors)],
            "borderColor": border_colors[i % len(border_colors)],
            "borderWidth": 1,
        }
        datasets.append(dataset)
    return datasets


def get_apps(developer_id: str) -> List[str]:
    """
    Get a list of app IDs associated with a given developer ID
    """
    try:
        query = {"user": ObjectId(developer_id)}
        results = app_collection.find(query)
        app_ids = [str(result["_id"]) for result in results]
        return app_ids
    except Exception as e:
        logger.log(
            service_name=SERVICE_NAME, level=3, msg=f"Error fetching apps: {str(e)}"
        )
        print("Error while fetching apps ")
        return []


def get_sensor_data(sensor_type: str, count: int = 3, numTimestamps: int = 5):
    """
    Get sensor data for a given sensor type and number of sensors

    Args:
    - sensor_type: str - the type of sensor to fetch data for
    - count: int - the number of sensors to fetch data for
    - numTimestamps: int - the number of timestamps to fetch data for

    Returns:
    - Tuple[List[str], dict] - a tuple containing a list of sensor IDs and a dictionary of sensor data
    """
    try:
        # Fetch sensor IDs for the given sensor type
        sensor_ids = fetchdata(
            {"readingtype": sensor_type, "numofsensors": count, "data_flag": False}
        )

        # Initialize data dictionary
        sensor_data = {}
        inner_dict_arr = []

        # Fetch data for each sensor ID
        obj = fetchdata({"numofsensors": count, "sensorIDs": sensor_ids})
        json_formatted_str = json.dumps(obj, indent=4)

        # Process data for each sensor ID
        for sensor_id in sensor_ids:
            field_names = obj[sensor_id]["fields"]
            data = obj[sensor_id]["data"]
            data = data[:numTimestamps]
            field_values, values = [], []
            for i in range(numTimestamps):
                curr_entry_values = list(data[i].values())[
                    :-1
                ]  # ignoring the version value
                values.append(curr_entry_values)
            field_values = np.array(values).T
            field_values = field_values.tolist()
            inner_dict = {k: v for k, v in zip(field_names, field_values)}
            inner_dict_arr.append(inner_dict)

        # Populate data dictionary with processed data
        sensor_data = {k: v for k, v in zip(sensor_ids, inner_dict_arr)}

        # Save data to file (for testing purposes)
        with open("response.json", "w") as f:
            f.write(json_formatted_str)
        with open("final_response.json", "w") as f:
            f.write(json.dumps(sensor_data, indent=4))

        # Return sensor IDs and data dictionary
        return sensor_ids, sensor_data
    except Exception as e:
        print(f"Error fetching sensor data: {str(e)}")
        return [], {}


print("Analitics Service Started....")
logger.log(
    service_name=SERVICE_NAME,
    level=1,
    msg="Analitics Service Started....",
)


@router.get("/analytics/waterSensor/pressureVoltage")
async def generate_performance_analysis_chart(
    developer_id: str, app_id: str, numSensors: int = 1, numTimeStamps: int = 5
):
    if developer_id is None or app_id is None:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg="Error: Developer ID and App ID are required fields in '/analytics/waterSensor/pressureVoltage'. ",
        )
        return HTMLResponse(
            content="Error: Developer ID and App ID are required fields",
            status_code=400,
        )

    if not is_valid_developer(developer_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: Developer not found in '/analytics/waterSensor/pressureVoltage'. ",
        )
        return HTMLResponse(content="Error: Developer not found", status_code=404)

    if not is_valid_app(developer_id, app_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: App not found for this developer in '/analytics/waterSensor/pressureVoltage'. ",
        )
        return HTMLResponse(
            content="Error: App not found for this developer", status_code=404
        )

    try:
        # Call the function to get sensor data and labels
        sensor_ids, data_dict = get_sensor_data("Flowrate", numSensors, numTimeStamps)

        # Create a list to store the data and labels for each sensor
        data_list = []
        label_list = []

        # Loop through each sensor ID and get the data and labels
        for i in range(len(sensor_ids)):
            data = data_dict[sensor_ids[i]]["Pressure Voltage"]
            timestamps = data_dict[sensor_ids[i]]["Timestamp"]
            labels = format_timestamps(timestamps)

            # Append the data and labels to the respective lists
            data_list.append(data)
            label_list.append(labels)

        # Generate the datasets using the data list
        data = generate_datasets(data_list)

        chart_html = """
        <html>
        <head>
        <title>Bar Chart</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
        <canvas id="barChart" width="400" height="400"></canvas>
        <script>
        var ctx = document.getElementById('barChart').getContext('2d');
        let delayed;
        var chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: %s,
                datasets: %s
            },
            options: {
                responsive: true,
                animation: {
                    onComplete: () => {
                        delayed = true;
                    },
                    delay: (context) => {
                        let delay = 0;
                        if (context.type === 'data' && context.mode === 'default' && !delayed) {
                            delay = context.dataIndex * 300 + context.datasetIndex * 100;
                        }
                        return delay;
                    },
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Water sensor - Pressure Voltage report'
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true
                    }
                }
            }
        });
        </script>
        </body>
        </html>
        """ % (
            label_list[0],
            str(data).replace("'", '"'),
        )

        return HTMLResponse(content=chart_html)

    except Exception as e:
        # Handle any exceptions that occur
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg=f"Error : {str(e)}. in 'water Sensor- pressure Voltage api' ",
        )
        return HTMLResponse(
            content=f"Error: Something missing/wrong: ", status_code=500
        )


@router.get("/analytics/waterSensor/heatmap")
async def generate_heatmap_chart(
    developer_id: str,
    app_id: str,
    fieldName="Total Flow",
    numSensors: int = 5,
    numTimeStamps: int = 10,
):
    if developer_id is None or app_id is None:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg="Error: Developer ID and App ID are required fields in '/analytics/waterSensor/heatmap'. ",
        )
        return HTMLResponse(
            content="Error: Developer ID and App ID are required fields",
            status_code=400,
        )
    if not is_valid_developer(developer_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: Developer not found in '/analytics/waterSensor/heatmap'. ",
        )
        return HTMLResponse(content="Error: Developer not found", status_code=404)

    if not is_valid_app(developer_id, app_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: App not found for this developer in '/analytics/waterSensor/heatmap'. ",
        )
        return HTMLResponse(
            content="Error: App not found for this developer", status_code=404
        )

    try:
        # Get data and labels from the data_dict based on developer_id and app_id
        sensor_ids, data_dict = get_sensor_data("Flowrate", numSensors, numTimeStamps)

        # Extract data for the first sensor and timestamps from the data_dict
        data = data_dict[sensor_ids[0]][fieldName]
        timestamps = data_dict[sensor_ids[0]]["Timestamp"]
        labels = format_timestamps(timestamps)

        # Check if data and labels are available
        if not labels or not data:
            raise Exception("Data not found")

        # Extract data for all the sensors and store them in a list
        data_list = []
        for sensor_id in sensor_ids:
            data_list.append(data_dict[sensor_id][fieldName])

        # Check if data is available for all the sensors
        if not all(data_list) or not labels:
            raise Exception("Data not found")

        # Generate series data and names dynamically based on data
        series = []
        series_names = []
        for i, row in enumerate(data_list):
            series.append({"name": f"Sensor {i+1}", "data": row})
            series_names.append(f"Sensor {i+1}")

        chart_data = {
            "chart": {
                "type": "heatmap",
                "height": 400,
                "width": 700,
                "toolbar": {"show": True},
            },
            "plotOptions": {
                "heatmap": {
                    "shadeIntensity": 0.5,
                    "colorScale": {
                        "ranges": [
                            {"from": 0, "to": 20, "name": "Low", "color": "#FF0000"},
                            {
                                "from": 21,
                                "to": 50,
                                "name": "Medium",
                                "color": "#FFA500",
                            },
                            {"from": 51, "to": 100, "name": "High", "color": "#00FF00"},
                        ]
                    },
                }
            },
            "series": series,
            "options": {
                "responsive": True,
                "legend": {"show": False},
                "title": {
                    "text": "Heatmap Chart",
                    "align": "left",
                },
                "xaxis": {
                    "categories": labels,
                    "title": {"text": "Timestamp"},
                    "labels": {
                        "show": True,  # Set the show attribute to True to show the x-axis labels
                        "style": {
                            # Set the color of the x-axis labels
                            "colors": ["#007875"]
                        },
                    },
                    "columns": labels,  # Add the labels variable as columns
                },
                "yaxis": {"title": {"text": "Sensors"}},
            },
        }

        chart_html = """
        <html>
            <head>
                <title>Heatmap Chart with ApexCharts</title>
                <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
            </head>
            <body>
                <h5><center>Water sensor - Data report</center></h5> 
                <div id="chart"></div>
                <script>
                    var chart = new ApexCharts(document.querySelector("#chart"), %s);
                    chart.render();
                </script>
            </body>
        </html>
        """ % json.dumps(
            chart_data
        )

        return HTMLResponse(content=chart_html)

    except Exception as e:
        # Return an error response if there is any exception
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg=f"Error : {str(e)}. in 'water Sensor - heatmap api' ",
        )
        return HTMLResponse(content="Error: Something missing/wrong", status_code=404)


# SMART ROOM API'S# Energy - Line Chart
@router.get("/analytics/smartRoom/energy")
async def generate_line_chart(
    developer_id, app_id, numSensors: int = 3, numTimeStamps: int = 15
):
    if developer_id is None or app_id is None:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg="Error: Developer ID and App ID are required fields in '/analytics/smartRoom/energy'. ",
        )
        return HTMLResponse(
            content="Error: Developer ID and App ID are required fields",
            status_code=400,
        )
    if not is_valid_developer(developer_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: Developer not found in '/analytics/smartRoom/energy'. ",
        )
        return HTMLResponse(content="Error: Developer not found", status_code=404)

    if not is_valid_app(developer_id, app_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: App not found for this developer in '/analytics/smartRoom/energy'. ",
        )
        return HTMLResponse(
            content="Error: App not found for this developer", status_code=404
        )

    try:
        # Get data and labels from the data_dict based on developer_id and app_id
        sensor_ids, data_dict = get_sensor_data("Energy", numSensors, numTimeStamps)
        datasets = []
        for i in range(numSensors):
            data = data_dict[sensor_ids[i]]["Energy"]
            timestamps = data_dict[sensor_ids[i]]["Timestamp"]
            labels = format_timestamps(timestamps)

            # Check if data and labels are available
            if not labels or not data:
                raise Exception(f"Data not found for sensor {sensor_ids[i]}")

            datasets.append(
                {
                    "label": f"Sensor {sensor_ids[i]}",
                    "data": data,
                    "backgroundColor": f"rgba({i*50}, {i*100}, {i*150}, 0.6)",
                    "borderColor": f"rgba({i*50}, {i*100}, {i*150}, 1)",
                    "borderWidth": 1,
                }
            )

        chart_html = """
        <html>
            <head>
                <title>Line Chart with Animation</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
                <canvas id="lineChart" width="400" height="400"></canvas>
                <script>
                    var ctx = document.getElementById('lineChart').getContext('2d');
                    var chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: %s,
                            datasets: %s
                        },
                        options: {
                            responsive: true,
                            animation: {
                                duration: 2000, // Animation duration in milliseconds
                                easing: 'easeOutQuart' // Animation easing function
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Smart Room Energy Monitoring - Energy'
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    stacked: true
                                }
                            }
                        }
                    });
                </script>
            </body>
        </html>
        """ % (
            labels,
            datasets,
        )

        return HTMLResponse(content=chart_html)

    except Exception as e:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg=f"Error : {str(e)}. in 'Smart room - Energy api' ",
        )
        return HTMLResponse(content="Error: Something missing/wrong", status_code=404)


# Power - Doughnut/Gauge Chart
@router.get("/analytics/smartRoom/power")
async def generate_doughnut_chart(
    developer_id, app_id, numSensors: int = 1, numTimeStamps: int = 5
):
    numSensors = 1
    if developer_id is None or app_id is None:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg="Error: Developer ID and App ID are required fields in '/analytics/smartRoom/power'. ",
        )
        return HTMLResponse(
            content="Error: Developer ID and App ID are required fields",
            status_code=400,
        )
    if not is_valid_developer(developer_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: Developer not found in '/analytics/smartRoom/power'. ",
        )
        return HTMLResponse(content="Error: Developer not found", status_code=404)

    if not is_valid_app(developer_id, app_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: App not found for this developer in '/analytics/smartRoom/power'. ",
        )
        return HTMLResponse(
            content="Error: App not found for this developer", status_code=404
        )

    try:
        # Get data and labels from the data_dict based on developer_id and app_id
        sensor_ids, data_dict = get_sensor_data("Energy", numSensors, numTimeStamps)

        # Extract Power data and Timestamp labels for the first sensor_id
        data = data_dict[sensor_ids[0]]["Power"]
        timestamps = data_dict[sensor_ids[0]]["Timestamp"]
        labels = format_timestamps(timestamps)

        # Check if data and labels are available
        if not labels or not data:
            raise Exception("Data not found")

        chart_html = """
        <html>
            <head>
                <title>doughnut/Guage Chart with Animation</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
                <canvas id="doughnut_chart" width="400" height="400"></canvas>
                <script>
                    var ctx = document.getElementById('doughnut_chart').getContext('2d');
                    var chart = new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: %s,
                            datasets: [{
                                label: 'Data',
                                data: %s,
                                backgroundColor: [
                                    'rgba(255, 99, 132, 0.5)',
                                    'rgba(54, 162, 235, 0.5)',
                                    'rgba(255, 206, 86, 0.5)',
                                    'rgba(75, 192, 192, 0.5)',
                                    'rgba(153, 102, 255, 0.5)',
                                    'rgba(255, 159, 64, 0.5)'
                                ],
                                borderColor: [
                                    'rgba(255, 99, 132, 1)',
                                    'rgba(54, 162, 235, 1)',
                                    'rgba(255, 206, 86, 1)',
                                    'rgba(75, 192, 192, 1)',
                                    'rgba(153, 102, 255, 1)',
                                    'rgba(255, 159, 64, 1)'
                                ],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                        
                            rotation: 270, // start angle in degrees
                            circumference: 180, // sweep angle in degrees
                            animation: {
                                duration: 5000, // Animation duration in milliseconds
                                easing: 'easeInOutElastic' // Animation easing function
                            },
                            plugins: {
                                legend: {
                                position: 'top',
                                },
                                title: {
                                display: true,
                                text: '  Smart Room Energy Monitoring - Power'
                                },
                            }
                        }
                    });
                </script>
            </body>
        </html>
        """ % (
            labels,
            data,
        )

        return HTMLResponse(content=chart_html)

    except Exception as e:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg=f"Error : {str(e)}. in 'Smart room - power api' ",
        )
        return HTMLResponse(content="Error: Something missing/wrong", status_code=404)


# Current - Circle radius bar chart
@router.get("/analytics/smartRoom/current")
async def generate_circle_radius_bar_chart(
    developer_id, app_id, numSensors: int = 1, numTimeStamps: int = 5
):
    if developer_id is None or app_id is None:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg="Error: Developer ID and App ID are required fields in '/analytics/smartRoom/current'. ",
        )
        return HTMLResponse(
            content="Error: Developer ID and App ID are required fields",
            status_code=400,
        )
    if not is_valid_developer(developer_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: Developer not found in '/analytics/smartRoom/current'. ",
        )
        return HTMLResponse(content="Error: Developer not found", status_code=404)

    if not is_valid_app(developer_id, app_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: App not found for this developer in '/analytics/smartRoom/current'. ",
        )
        return HTMLResponse(
            content="Error: App not found for this developer", status_code=404
        )

    try:
        # Get sensor data from the data_dict based on developer_id and app_id
        sensor_ids, data_dict = get_sensor_data("Energy", numSensors, numTimeStamps)

        # Get current data and labels from the data_dict
        data = data_dict[sensor_ids[0]]["Current"]
        timestamps = data_dict[sensor_ids[0]]["Timestamp"]
        labels = format_timestamps(timestamps)

        # Check if data and labels are available
        if not labels or not data:
            raise ValueError("Data not found")

        chart_data = {
            "chart": {
                "type": "radialBar",
                "height": 600,  # Set the height of the chart
                "width": 600,
                "toolbar": {"show": True},  # Show the toolbar
            },
            "series": data,
            "labels": labels,
            "colors": [
                "#FF6384",
                "#36A2EB",
                "#FFCE56",
                "#4BC0C0",
                "#9966FF",
                "#FF9F40",
            ],
            "plotOptions": {
                "radialBar": {
                    "startAngle": -90,
                    "endAngle": 90,
                    "track": {
                        "background": "#f8f8f8",
                        "startAngle": -90,
                        "endAngle": 90,
                    },
                    "dataLabels": {
                        "name": {
                            "fontSize": "16px",
                            "color": "#000",
                            "fontWeight": 600,
                            "show": True,
                        },
                        "value": {
                            "fontSize": "14px",
                            "color": "#000",
                            "fontWeight": 400,
                            "show": True,
                        },
                    },
                    "barHeight": "80%",
                    "distributed": True,
                    "barWidth": 10,
                }
            },
            "options": {
                "responsive": True,
                "legend": {"show": False},
                "title": {
                    "text": "Circle Radius Bar Chart",  # Update the chart title
                    # Add alignment for chart title (left, center, right)
                    "align": "left",
                },
                "subtitle": {
                    "text": "Subtitle text goes here",  # Add a subtitle
                    # Add alignment for subtitle (left, center, right)
                    "align": "left",
                },
            },
        }

        chart_html = """
        <html>
            <head>
                <title>Circle Radius Bar Chart with ApexCharts</title>
                <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
            </head>
            <body>
            <h5><center> Smart Room Energy Monitoring - Current</center></h5> 
                <div id="chart"></div>
                <script>
                    var chart = new ApexCharts(document.querySelector("#chart"), %s);
                    chart.render();
                </script>
            </body>
        </html>
        """ % json.dumps(
            chart_data
        )

        return HTMLResponse(content=chart_html)
    except KeyError as e:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg=f"Error : {str(e)}. in 'Smart room - Current api' ",
        )
        return HTMLResponse(content=f"KeyError: {e}", status_code=404)

    except ValueError as e:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg=f"Error : {str(e)}. in 'Smart room - Current api' ",
        )
        return HTMLResponse(content=f"{e}", status_code=404)

    except Exception as e:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg=f"Error : {str(e)}. in 'Smart room - Current api' ",
        )
        return HTMLResponse(content="Error: Something missing/wrong", status_code=500)


# SOLAR MONITORING API's
@router.get("/analytics/solarMonitor/heatmap")
async def generate_heatmap_chart2(developer_id, app_id):
    numTimeStamps = 1
    if developer_id is None or app_id is None:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg="Error: Developer ID and App ID are required fields in '/analytics/solarMonitor/heatmap'. ",
        )
        return HTMLResponse(
            content="Error: Developer ID and App ID are required fields",
            status_code=400,
        )
    if not is_valid_developer(developer_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: Developer not found in '/analytics/solarMonitor/heatmap'. ",
        )
        return HTMLResponse(content="Error: Developer not found", status_code=404)

    if not is_valid_app(developer_id, app_id):
        logger.log(
            service_name=SERVICE_NAME,
            level=1,
            msg="Error: App not found for this developer in '/analytics/solarMonitor/heatmap'. ",
        )
        return HTMLResponse(
            content="Error: App not found for this developer", status_code=404
        )

    try:
        # Get data from the data_dict based on developer_id and app_id
        sensor_ids, data_dict = get_sensor_data("Voltage1", 1, numTimeStamps)

        data = []
        voltage_data = [
            data_dict[sensor_ids[0]]["Voltage1"][0],
            data_dict[sensor_ids[0]]["Voltage2"][0],
            data_dict[sensor_ids[0]]["Voltage3"][0],
        ]
        current_data = [
            data_dict[sensor_ids[0]]["Current1"][0],
            data_dict[sensor_ids[0]]["Current2"][0],
            data_dict[sensor_ids[0]]["Current3"][0],
        ]
        power_data = [
            data_dict[sensor_ids[0]]["Power1"][0],
            data_dict[sensor_ids[0]]["Power2"][0],
            data_dict[sensor_ids[0]]["Power3"][0],
        ]

        data.append(voltage_data)
        data.append(current_data)
        data.append(power_data)

        labels = list(map(str, [1, 2, 3]))

        # Check if data is available
        if not data or not labels:
            return HTMLResponse(content="Data not found", status_code=404)

        # Generate series data and names dynamically based on data
        series = []
        series_names = ["Voltage", "Current", "Power"]
        for name, row in zip(series_names, data):
            series.append({"name": name, "data": row})

        chart_data = {
            "chart": {
                "type": "heatmap",
                "height": 400,  # Set the height of the chart
                "width": 700,
                "toolbar": {"show": True},  # Show the toolbar
            },
            "plotOptions": {
                "heatmap": {
                    "shadeIntensity": 0.5,
                    "colorScale": {
                        "ranges": [
                            {"from": 0, "to": 20, "name": "Low", "color": "#FF0000"},
                            {
                                "from": 21,
                                "to": 50,
                                "name": "Medium",
                                "color": "#FFA500",
                            },
                            {"from": 51, "to": 100, "name": "High", "color": "#00FF00"},
                        ]
                    },
                }
            },
            "series": series,
            "options": {
                "responsive": True,
                "legend": {"show": False},
                "title": {
                    "text": "Solar monitor sensor data report",  # Update the chart title
                    # Add alignment for chart title (left, center, right)
                    "align": "left",
                },
                "subtitle": {
                    "text": "Subtitle text goes here",  # Add a subtitle
                    # Add alignment for subtitle (left, center, right)
                    "align": "left",
                },
                "xaxis": {
                    "categories": labels,
                    "title": {"text": "Sensors"},  # Add x-axis title here
                },
                "yaxis": {
                    # Update Y-axis title
                    "title": {"text": "Y-axis title goes here"}
                },
            },
        }

        chart_html = """
        <html>
            <head>
                <title>Heatmap Chart with ApexCharts</title>
                <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
            </head>
            <body>
                <h5><center>Solar monitor sensor data report</center></h5> 
                <div id="chart"></div>
                <script>
                    var chart = new ApexCharts(document.querySelector("#chart"), %s);
                    chart.render();
                </script>
            </body>
        </html>
        """ % json.dumps(
            chart_data
        )

        return HTMLResponse(content=chart_html)

    except Exception as e:
        logger.log(
            service_name=SERVICE_NAME,
            level=2,
            msg=f"Error : {str(e)}. in 'Solar Monitor - heatmap api' ",
        )
        return HTMLResponse(content="Error: Something missing/wrong", status_code=500)
