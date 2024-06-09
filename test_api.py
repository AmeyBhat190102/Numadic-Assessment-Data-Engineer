import requests

# Define the API endpoint
url = 'http://127.0.0.1:5000/generate_report'  # Update the URL if the Flask app is hosted elsewhere

# JSON data with start_time and end_time
data = {
    'start_time': '1527618557',  # Example start time
    'end_time': '20180312172929'      # Example end time
}

# Make a POST request to the API endpoint
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Extract the JSON data from the response
    report_data = response.json()
    print(report_data)
else:
    print('Error:', response.status_code)

