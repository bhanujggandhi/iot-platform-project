# Analytics Module

## Sensor Analytics API

This project provides a set of RESTful APIs for generating various analytics charts based on the sensor data collected from different types of sensors. Currently, the project supports three types of sensors:

- Water Quality Sensors
- Smart Room Energy Monitoring Sensors
- Solar Monitoring Sensors

## Water Quality API's

### Pressure Voltage Chart

- Endpoint: `/analytics/waterSensor/pressureVoltage`
- Description: This API generates a line chart showing the pressure voltage readings from the water quality sensors for a specific field.
- Parameters:
  - `developer_id`: The ID of the developer. Required.
  - `app_id`: The ID of the application. Required.
  - `sensor_type`: The type of the sensor. Optional. Default is `flowrate`.
  - `numSensors`: The number of sensors to be included in the chart. Optional. Default is 3.
  - `numTimeStamps`: The number of time stamps to be included in the chart. Optional. Default is 10.

### Heatmap Chart

- Endpoint: `/analytics/waterSensor/heatmap`
- Description: This API generates a heatmap chart showing the readings from the water quality sensors for a specific field.
- Parameters:
  - `developer_id`: The ID of the developer. Required.
  - `app_id`: The ID of the application. Required.
  - `fieldName`: The name of the field to be shown in the chart. Optional. Default is `Total Flow`.
  - `numSensors`: The number of sensors to be included in the chart. Optional. Default is 5.
  - `numTimeStamps`: The number of time stamps to be included in the chart. Optional. Default is 10.

## Smart Room API's

### Energy Line Chart

- Endpoint: `/analytics/smartRoom/energy`
- Description: This API generates a line chart showing the energy readings from the smart room energy monitoring sensors.
- Parameters:
  - `developer_id`: The ID of the developer. Required.
  - `app_id`: The ID of the application. Required.
  - `numSensors`: The number of sensors to be included in the chart. Optional. Default is 3.
  - `numTimeStamps`: The number of time stamps to be included in the chart. Optional. Default is 15.

### Power Doughnut/Gauge Chart

- Endpoint: `/analytics/smartRoom/power`
- Description: This API generates a doughnut or gauge chart showing the power readings from the smart room energy monitoring sensors.
- Parameters:
  - `developer_id`: The ID of the developer. Required.
  - `app_id`: The ID of the application. Required.
  - `numSensors`: The number of sensors to be included in the chart. Optional. Default is 1.
  - `numTimeStamps`: The number of time stamps to be included in the chart. Optional. Default is 5.

### Current Circle Radius Bar Chart

- Endpoint: `/analytics/smartRoom/current`
- Description: This API generates a circle radius bar chart showing the current readings from the smart room energy monitoring sensors.
- Parameters:
  - `developer_id`: The ID of the developer. Required.
  - `app_id`: The ID of the application. Required.
  - `numSensors`: The number of sensors to be included in the chart. Optional. Default is 1.
  - `numTimeStamps`: The number of time stamps to be included in the chart. Optional. Default is 5.

## Solar Monitoring API's

### Heatmap Chart

- Endpoint: `/analytics/solarMonitor/heatmap`
- Description: This API generates a heatmap chart showing the readings from the solar monitoring sensors.
- Parameters:
  - `developer_id` (required): The ID of the developer.
  - `app_id` (required): The ID of the app.

## Command to run application with uvicorn  

```bash
    python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 9001
```