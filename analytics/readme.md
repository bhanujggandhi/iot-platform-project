# Analytics Module:

1. Line Chart
This type of chart is commonly used to display trends over time. It can be useful for showing how certain variables or metrics change over a period of time, such as sensor data, temperature readings, or other time-series data.
* ` Status: done... `

2. Bar Chart
A bar chart is a great option for displaying data in categories or groups. It can be used to compare different data points, such as sensor readings from multiple devices, app usage statistics, or other categorical data.
* ` Status: done... `

3. Pie Chart
A pie chart is a circular chart that is commonly used to display data as a proportion of a whole. It can be used to show percentage distribution of different data points, such as device types, sensor types, or other categorical data.
* ` Status: done... `

4. Area Chart
An area chart is similar to a line chart, but it fills the area under the line with color, which can help to emphasize the magnitude of change over time. It can be useful for showing cumulative data, such as total usage or total revenue.
* ` Status: done... ` (may be not required, will see later)*

5. Gauge Chart
A gauge chart is a type of chart that resembles a speedometer or gauge, and is used to display a single value within a defined range. It can be used to show real-time data, such as current sensor readings or other single-value metrics.
* ` Status: done... `

6. Radial Chart
A radial chart is a type of chart that displays data in a circular format, with values represented as points or bars radiating out from a central point. It can be used to show multi-dimensional data or relationships between different variables.
* ` Status: done... `

7. Scatter Plot
A scatter plot is used to display the relationship between two variables, with one variable plotted on the x-axis and the other on the y-axis. It can be used to show correlations or patterns in data, such as sensor data from different devices or other related variables.
* `` Status: Not done... ``

8. Heatmap
A heatmap is a graphical representation of data where values are represented as colors in a matrix or grid format. It can be used to display data patterns or density, such as device usage across different locations or other spatial data.
* ` Status: done... `


-- Command to run application with uvicorn:
```bash
python3 -m uvicorn graphs:app --reload --host 0.0.0.0 --port 8001