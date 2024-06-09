# Flask Asset Report Generator

## Overview
This Flask application generates asset reports based on vehicle location data. It calculates various metrics such as distance traveled, number of trips completed, average speed, and speed violations.

## Prerequisites
- Python 
- Flask
- pandas
- zipfile

## Usage
1. Place the `NU-raw-location-dump.zip` file containing the raw location data in the project directory.
2. Ensure that the `Trip-Info.csv` file containing trip information is also present in the project directory.
3. Run the Flask application:

## API Endpoint
- **/generate_report**: 
    - Method: POST
    - Payload: JSON object containing `start_time` and `end_time` for the report generation.
    - Example Payload:
    ```json
    {
        "start_time": "1527618557",
        "end_time": "20180312172929"
    }
    ```
    - Response: JSON object containing the generated report or error message.

## Error Handling
- If an error occurs during report generation, the API will return an error message along with a 500 status code.
- Error messages provide detailed information about the type of error that occurred.
