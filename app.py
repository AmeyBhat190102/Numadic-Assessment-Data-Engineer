from flask import Flask, request, jsonify
import zipfile
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import os
import shutil
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    try:
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.

        return c * r,
    except Exception as e:
        return None


def generate_asset_report(start_time, end_time):
    try:
        with zipfile.ZipFile('NU-raw-location-dump.zip', 'r') as zip_ref:
            zip_ref.extractall('vehicle_trails')

        trip_info_df = pd.read_csv('Trip-Info.csv', parse_dates=['date_time'])

        report_df = pd.DataFrame(columns=[
            'License plate number', 'Distance', 'Number of Trips Completed',
            'Average Speed', 'Transporter Name', 'Number of Speed Violations',
            'Max Speed', 'Min Speed'
        ])

        for csv_file in os.listdir('vehicle_trails/EOL-dump'):
            if csv_file.endswith('.csv'):
                print("Processing for {}".format(csv_file))
                trail_df = pd.read_csv(os.path.join('vehicle_trails/EOL-dump/', csv_file))
                trail_df["tis"] = trail_df["tis"].astype(str)
                filtered_trail = trail_df[(trail_df['tis'] >= start_time) & (trail_df['tis'] <= end_time)]
                trail_df["tis"] = trail_df["tis"].astype(int)

                if not filtered_trail.empty:
                    filtered_trail['lat_shifted'] = filtered_trail['lat'].shift(1)
                    filtered_trail['lon_shifted'] = filtered_trail['lon'].shift(1)

                    filtered_trail['distance'] = filtered_trail.apply(lambda row: haversine(row['lat'], row['lon'],
                                                                                            row['lat_shifted'],
                                                                                            row['lon_shifted']), axis=1)
                    total_distance = filtered_trail['distance'].sum()
                    speed_violations = filtered_trail['osf'].sum()
                    vehicle_number = filtered_trail['lic_plate_no'].iloc[0]
                    transporter_info = trip_info_df[trip_info_df['vehicle_number'] == vehicle_number]
                    if len(transporter_info):
                        transporter_name = transporter_info['transporter_name'].iloc[0]
                    else:
                        transporter_name = None
                    num_trips_completed = len(transporter_info)
                    average_speed = filtered_trail['spd'].mean()
                    max_speed = filtered_trail['spd'].max()
                    min_speed = filtered_trail['spd'].min()

                    report_row = pd.DataFrame({
                        'License plate number': [vehicle_number],
                        'Distance': [total_distance],
                        'Number of Trips Completed': [num_trips_completed],
                        'Average Speed': [average_speed],
                        'Transporter Name': [transporter_name],
                        'Number of Speed Violations': [speed_violations],
                        'Max Speed': [max_speed],
                        'Min Speed': [min_speed],
                    })

                    report_df = pd.concat([report_df, report_row], ignore_index=True)
                    print("Dimensions of Report DF : ", len(report_df))

        if len(report_df):
            return report_df, None
        else:
            return None, "Data was not available for generating a Report! Try with another date range"
    except Exception as e:
        return None, str(e)


@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        req_data = request.get_json()
        start_time = req_data['start_time']
        end_time = req_data['end_time']

        # Generate report
        report_df, error = generate_asset_report(start_time, end_time)

        if report_df is None:
            return jsonify({'error': f'An error occurred while generating the report. Error : {error}'}), 500

        # Convert report DataFrame to JSON
        report_json = report_df.to_json(orient='records')
        return jsonify(report_json)
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred. Error : {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
