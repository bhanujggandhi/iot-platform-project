# Monitoring Service

This is a monitoring service that tracks the health status of different modules in the system. The service is built using Python and uses MongoDB to store module health statuses. Kafka is used as the message broker between different modules.

### Dependencies

The following dependencies are required to run the service:

- Python 3.6 or higher
- requests library
- pymongo library
- kafka-python library
- decouple library

### Configuration

The configuration file `topic_info.json` contains information about the Kafka topics used by different modules. This file needs to be updated with the correct topic names before running the service.

### Running the Service

To run the service, execute the following command:

```bash
python3 monitoring_service.py

