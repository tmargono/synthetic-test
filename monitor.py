import aiohttp
import asyncio
import yaml
import time
import argparse
import pandas as pd
from urllib.parse import urlparse

# Function to read the YAML file and load the endpoints
def load_endpoints(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Async function to test the health of an HTTP endpoint
async def check_health(session, endpoint):
    url = endpoint.get('url')
    # Default method if not given is GET
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers', {})
    body = endpoint.get('body', None)

    try:
        start_time = time.time()

        # Make the request
        async with session.request(method.upper(), url, headers=headers, data=body) as response:
            latency = time.time() - start_time
            # Check if status code is in 2xx range and latency is less than 500ms
            if 200 <= response.status < 300 and latency < 0.5:
                return (urlparse(url).netloc, "UP")  # format: (DOMAIN, STATUS)
            else:
                return (urlparse(url).netloc, "DOWN")

    except aiohttp.ClientError:
        return (urlparse(url).netloc, "DOWN")  # Error so report DOWN

# Function to log the availability of each domain
def log_availability(df, domain_availability):
    # Loop through domains
    for domain, availability_percentage in domain_availability.items():
        # Add to total_requests and up_requests for the domain
        domain_availability[domain]['total_requests'] += len(df[df['domain'] == domain])
        domain_availability[domain]['up_requests'] += len(df[(df['domain'] == domain) & (df['status'] == 'UP')])
        
        # Calculate availability percentage for the domain
        availability_percentage = 100 * domain_availability[domain]['up_requests'] / domain_availability[domain]['total_requests']
        
        # Round to nearest whole percent
        print(f"{domain} has {round(availability_percentage)}% availability percentage")

# Main async function to check the health of endpoints and track availability
async def monitor_health(file_path):
    endpoints = load_endpoints(file_path)

    domain_availability = {}

    # Create an aiohttp session for making requests
    async with aiohttp.ClientSession() as session:
        while True:
            start_time = time.time()
            tasks = []
            for i,endpoint in enumerate(endpoints):
                # If scheme doesn't exist default to https
                if not urlparse(endpoint['url']).scheme:
                    endpoints[i]['url'] = "https://" + endpoints[i]['url']  
                tasks.append(check_health(session, endpoint))

            # Perform all checks concurrently
            results = await asyncio.gather(*tasks)

            # Initialize data which will be used to build the pandas DataFrame
            data = {
                "domain": [],
                "status": []
            }

            for i, (domain, status) in enumerate(results):
                # Add domain and corresponding status to data
                data["domain"].append(domain)
                data["status"].append(status)

                # Initialize domain availability if this is first time domain is seen
                if domain not in domain_availability:
                    domain_availability[domain] = {'total_requests': 0, 'up_requests': 0}

            # Create pandas DataFrame
            df = pd.DataFrame(data)

            # Log the availability percentage for each domain
            log_availability(df, domain_availability)

            # Calculate elapsed time to adjust sleep duration
            # If it has already been at least 15 sec since the requests were started then just start the next check
            elapsed_time = time.time() - start_time
            await asyncio.sleep(max(0, 15 - elapsed_time))

if __name__ == "__main__":
    # Set up argument parsing to get the endpoint YAML file
    parser = argparse.ArgumentParser(description="Monitor the health of endpoints listed in a YAML file")
    parser.add_argument("endpoint_file", type=str, help="Path to the YAML file containing endpoints")
    args = parser.parse_args()

    file_path = args.endpoint_file

    try:
        # Run the monitoring in an asyncio event loop
        asyncio.run(monitor_health(file_path))
    except KeyboardInterrupt:
        print("Monitoring stopped manually")
