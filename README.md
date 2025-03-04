# Endpoint Health Monitor

This Python script monitors the health of endpoints by making asynchronous requests and tracking their availability over time.

## Features

Uses aiohttp for asynchronous requests. Requests are made to endpoints every 15 seconds.

Logs domain availability percentages over time.

Uses a Pandas DataFrame to process data.

## Installation

1. Clone the Repository

```
git clone https://github.com/tmargono/synthetic-test.git or git clone git@github.com:tmargono/synthetic-test.git
cd synthetic-test
```

2. If needed, install Python: https://www.python.org/downloads/

3. Install Dependencies

```
pip3 install aiohttp pyyaml pandas
```

4. Prepare the Endpoints Configuration File

Create a YAML file (such as endpoints.yaml) with the endpoints to monitor. Example:

```
- name: Example URL
  url: https://example.com
  method: GET
```

See `endpoints.yaml` for an example.

5. Run the Script

```
python3 monitor.py endpoints.yaml
```

To stop the monitoring, press CTRL+C.
