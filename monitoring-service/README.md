# Monitoring Service

## About

This is a monitoring service that tracks the health status of different modules in the system. The service is built using Python and uses MongoDB to store module health statuses. Kafka is used as the message broker between different modules.

### Dependencies

The following dependencies are required to run the service:

- Python 3.6 or higher
- requests library
- pymongo library
- kafka-python library
- decouple library

### Configuration

The configuration file `topic_info.json` contains information about the Kafka topics used by different modules. When a module wants to use this service, can use Heartbeat service with their module name and topic name available in `topic_info.json` .

### Running the Service

To run the service, execute the following command:

```bash
cd monitoring-service
python3 main.py
```

## Heartbeat Service

Use this module to implement a heartbeat service that responds to health check requests from a monitoring service.

### Instructions

1. Copy and paste `kafka_setup_config.json`, `logger_utils.py`, `Messenger.py` and `heartbeat_service.py` into your directory where `main.py` is running.

2. Import the following:

```py
import threading
from heartbeat_service import HeartbeatService
```

3. Initialize the HeartbeatService object with your Kafka topic name and your service name:

```py
TOPIC = "<your-topic-name>" # Replace with your topic name
SERVICE_NAME = "<your-service-name>" # Replace with your service name

# Create a new instance of the HeartbeatService class
heartbeat_service = HeartbeatService(TOPIC, SERVICE_NAME)
```

4. Start the heartbeat service as a thread:

```py
# Create a new thread and start the HeartbeatService instance
thread = threading.Thread(target=heartbeat_service.start)
thread.daemon = True
thread.start()
```