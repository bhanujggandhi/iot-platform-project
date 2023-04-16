import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# Example dictionary to store data for different developers and apps
data_dict = {
    "developer1": {
        "app1": {
            "labels": ["APi 1", "APi 2", "Api 3"],
            "data": [10, 60, 40]
        },
        "app2": {
            "labels": ["Label 1", "Label 2", "Label 3"],
            "data": [40, 20, 85]
        }
    },
    "developer2": {
        "app1": {
            "labels": ["Label 1", "Label 2", "Label 3"],
            "data": [30, 40, 50]
        },
        "app2": {
            "labels": ["Label 1", "Label 2", "Label 3"],
            "data": [20, 10, 5]
        }
    }
}


data_dict_gauge = {
    "developer_id_1": {
        "app_id_1": {
            "value": 75,
            "max": 100,
            "color": "rgba(75, 192, 192, 0.5)",
            "borderColor": "rgba(75, 192, 192, 1)"
        }
    }
}

data_dict_heatmap = {
    "developer1": {
        "app1": {
            "data":[
                        [30, 40, 50, 60, 70],
                        [20, 25, 30, 35, 40],
                        [10, 15, 20, 25, 30],
                        [5, 10, 15, 20, 25],
                        [0, 5, 10, 15, 20]
]
        },
        # Add more app_id data here
    },
    # Add more developer_id data here
}

# APIs for different graphs..
@app.get("/graph/performance_analysis/{developer_id}/{app_id}")
async def generate_performance_analysis_chart(developer_id: str, app_id: str):
    # Get data and labels from the data_dict based on developer_id and app_id
    labels = data_dict.get(developer_id, {}).get(app_id, {}).get("labels", [])
    data = data_dict.get(developer_id, {}).get(app_id, {}).get("data", [])

    # Check if data and labels are available
    if not labels or not data:
        return HTMLResponse(content="Data not found", status_code=404)

    chart_html = '''
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
                        datasets: [{
                            label: 'Data',
                            data: %s,
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)'
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
                                text: ' Stacked Bar chart'
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
    ''' % (labels, data)

    return HTMLResponse(content=chart_html)


@app.get("/graph/sample_analysis/{developer_id}/{app_id}")
async def generate_line_chart(developer_id: str, app_id: str):

    # Get data and labels from the data_dict based on developer_id and app_id
    labels = data_dict.get(developer_id, {}).get(app_id, {}).get("labels", [])
    data = data_dict.get(developer_id, {}).get(app_id, {}).get("data", [])

    # Check if data and labels are available
    if not labels or not data:
        return HTMLResponse(content="Data not found", status_code=404)

    chart_html = '''
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
                        datasets: [{
                            label: 'Data',
                            data: %s,
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)'
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
                        animation: {
                            duration: 2000, // Animation duration in milliseconds
                            easing: 'easeOutQuart' // Animation easing function
                        },
                         plugins: {
                            title: {
                                display: true,
                                text: ' Stacked Line chart'
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
    ''' % (labels, data)

    return HTMLResponse(content=chart_html)


@app.get("/graph/pie_chart/{developer_id}/{app_id}")
async def generate_pie_chart(developer_id: str, app_id: str):
    # Get data and labels from the data_dict based on developer_id and app_id
    labels = data_dict.get(developer_id, {}).get(app_id, {}).get("labels", [])
    data = data_dict.get(developer_id, {}).get(app_id, {}).get("data", [])

    # Check if data and labels are available
    if not labels or not data:
        return HTMLResponse(content="Data not found", status_code=404)

    chart_html = '''
    <html>
        <head>
            <title>Pie Chart with Animation</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <canvas id="pieChart" width="400" height="400"></canvas>
            <script>
                var ctx = document.getElementById('pieChart').getContext('2d');
                var chart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: %s,
                        datasets: [{
                            label: 'Data',
                            data: %s,
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)'
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
                        animation: {
                            duration: 4000, // Animation duration in milliseconds
                            easing: 'easeOutQuart' // Animation easing function
                        },
                        plugins: {
                            legend: {
                            position: 'top',
                            },
                            title: {
                            display: true,
                            text: 'Pie Chart'
                            }
                        }
                    }
                });
            </script>
        </body>
    </html>
    ''' % (labels, data)

    return HTMLResponse(content=chart_html)


@app.get("/graph/doughnut_chart/{developer_id}/{app_id}")
async def generate_doughnut_chart(developer_id: str, app_id: str):
    # Get data and labels from the data_dict based on developer_id and app_id
    labels = data_dict.get(developer_id, {}).get(app_id, {}).get("labels", [])
    data = data_dict.get(developer_id, {}).get(app_id, {}).get("data", [])

    # Check if data and labels are available
    if not labels or not data:
        return HTMLResponse(content="Data not found", status_code=404)

    chart_html = '''
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
                            text: ' Doughnut/Guage Chart'
                            },
                        }
                    }
                });
            </script>
        </body>
    </html>
    ''' % (labels, data)

    return HTMLResponse(content=chart_html)


# trying apexchart js ..

@app.get("/graph/circle_radius_bar_chart/{developer_id}/{app_id}")
async def generate_circle_radius_bar_chart(developer_id: str, app_id: str):
    # Get data and labels from the data_dict based on developer_id and app_id
    labels = data_dict.get(developer_id, {}).get(app_id, {}).get("labels", [])
    data = data_dict.get(developer_id, {}).get(app_id, {}).get("data", [])

    # Check if data and labels are available
    if not labels or not data:
        return HTMLResponse(content="Data not found", status_code=404)

    chart_data = {
        "chart": {
            "type": "radialBar",
            "height": 300, # Set the height of the chart
            "toolbar": {
                "show": True # Show the toolbar
            }
        },
        "series": data,
        "labels": labels,
        "colors": [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#9966FF',
            '#FF9F40'
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
                        "fontSize": '16px',
                        "color": '#000',
                        "fontWeight": 600,
                        "show": True
                    },
                    "value": {
                        "fontSize": '14px',
                        "color": '#000',
                        "fontWeight": 400,
                        "show": True
                    },
                },
                "barHeight": "80%",
                "distributed": True,
                "barWidth": 10
            }
        },
        "options": {
            "responsive": True,
            "legend": {
                "show": False
            },
            "title": {
            "text": 'Circle Radius Bar Chart',  # Update the chart title
            "align": 'left'  # Add alignment for chart title (left, center, right)
            },
            "subtitle": {
                "text": 'Subtitle text goes here',  # Add a subtitle
                "align": 'left'  # Add alignment for subtitle (left, center, right)
            },
        }
    }

    chart_html = '''
    <html>
        <head>
            <title>Circle Radius Bar Chart with ApexCharts</title>
            <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        </head>
        <body>
        <h5><center>Circle Radius Bar Chart</center></h5> 
            <div id="chart"></div>
            <script>
                var chart = new ApexCharts(document.querySelector("#chart"), %s);
                chart.render();
            </script>
        </body>
    </html>
    ''' % json.dumps(chart_data)

    return HTMLResponse(content=chart_html)


@app.get("/graph/heatmap_chart/{developer_id}/{app_id}")
async def generate_heatmap_chart(developer_id: str, app_id: str):
    # Get data from the data_dict based on developer_id and app_id
    data = data_dict_heatmap.get(developer_id, {}).get(app_id, {}).get("data", [])

    # Check if data is available
    if not data:
        return HTMLResponse(content="Data not found", status_code=404)

    # Generate series data and names dynamically based on data
    series = []
    series_names = []
    for i, row in enumerate(data):
        series.append({
            "name": f"Series {i+1}",
            "data": row
        })
        series_names.append(f"Series {i+1}")

    chart_data = {
        "chart": {
            "type": "heatmap",
            "height": 300, # Set the height of the chart
            "toolbar": {
                "show": True # Show the toolbar
            }
        },
        "plotOptions": {
            "heatmap": {
                "shadeIntensity": 0.5,
                "colorScale": {
                    "ranges": [
                        {
                            "from": 0,
                            "to": 20,
                            "name": "Low",
                            "color": "#FF0000"
                        },
                        {
                            "from": 21,
                            "to": 50,
                            "name": "Medium",
                            "color": "#FFA500"
                        },
                        {
                            "from": 51,
                            "to": 100,
                            "name": "High",
                            "color": "#00FF00"
                        }
                    ]
                }
            }
        },
        "series": series,
        "options": {
            "responsive": True,
            "legend": {
                "show": False
            },
            "title": {
                "text": 'Heatmap Chart',  # Update the chart title
                "align": 'left'  # Add alignment for chart title (left, center, right)
            },
            "subtitle": {
                "text": 'Subtitle text goes here',  # Add a subtitle
                "align": 'left'  # Add alignment for subtitle (left, center, right)
            },
            "xaxis": {
                "categories": [  # Update categories based on your data
                    "Category 1",
                    "Category 2",
                    "Category 3",
                    "Category 4",
                    "Category 5"
                ]
            },
            "yaxis": {
                "title": {
                    "text": 'Y-axis title goes here'  # Update Y-axis title
                }
            }
        }
    }

    chart_html = '''
    <html>
        <head>
            <title>Heatmap Chart with ApexCharts</title>
            <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        </head>
        <body>
            <h5><center>Heatmap Chart</center></h5> 
            <div id="chart"></div>
            <script>
                var chart = new ApexCharts(document.querySelector("#chart"), %s);
                chart.render();
            </script>
        </body>
    </html>
    ''' % json.dumps(chart_data)

    return HTMLResponse(content=chart_html)


# To do  
# Line Chart: This type of chart is commonly used to display trends over time. 
# It can be useful for showing how certain variables or metrics change over a period of time, 
# such as sensor data, temperature readings, or other time-series data.
# done...

# Bar Chart: A bar chart is a great option for displaying data in categories or groups. 
# It can be used to compare different data points, such as sensor readings from multiple devices, 
# app usage statistics, or other categorical data.
# done...

# Pie Chart: A pie chart is a circular chart that is commonly used to display data as a 
# proportion of a whole. It can be used to show percentage distribution of different data 
# points, such as device types, sensor types, or other categorical data.
# done...

# Area Chart: An area chart is similar to a line chart, but it fills the area under the 
# line with color, which can help to emphasize the magnitude of change over time. 
# It can be useful for showing cumulative data, such as total usage or total revenue.
# done  may be not required will see later...

# Gauge Chart: A gauge chart is a type of chart that resembles a speedometer or gauge,
#  and is used to display a single value within a defined range. 
# It can be used to show real-time data, such as current sensor readings or 
# other single-value metrics.
# done...

# Radial Chart: A radial chart is a type of chart that displays data in a circular format,
#  with values represented as points or bars radiating out from a central point. It can be 
# used to show multi-dimensional data or relationships between different variables.
# done...


# Scatter Plot: A scatter plot is used to display the relationship between two variables,
#  with one variable plotted on the x-axis and the other on the y-axis. It can be used to 
# show correlations or patterns in data, such as sensor data from different devices or other
#  related variables.

# Heatmap: A heatmap is a graphical representation of data where values are represented as
#  colors in a matrix or grid format. It can be used to display data patterns or density,
#  such as device usage across different locations or other spatial data.
