import pandas
import numpy
import os
import glob
from collections import defaultdict

# Loading All CVS Files From The Temperatures Folder
def load_temperature_data(temperatures_folder):
    all_data = []
    station_data = defaultdict(list)
    
    csv_files = glob.glob(os.path.join(temperatures_folder, "*.csv"))
    
    print(f"Found {len(csv_files)} CSV files to process...")
    
    for file_path in csv_files:
        try:
            df = pandas.read_csv(file_path)
            print(f"Processing {os.path.basename(file_path)}...")
            
            for _, row in df.iterrows():
                station_name = row['STATION_NAME']
                
                monthly_temps = []
                for month in ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']:
                    temp = row[month]
                    if pandas.notna(temp):
                        monthly_temps.append(temp)
                        station_data[station_name].append(temp)

                all_data.append({
                    'station': station_name,
                    'year': os.path.basename(file_path).split('_')[-1].split('.')[0],
                    'jan': row['January'] if pandas.notna(row['January']) else None,
                    'feb': row['February'] if pandas.notna(row['February']) else None,
                    'mar': row['March'] if pandas.notna(row['March']) else None,
                    'apr': row['April'] if pandas.notna(row['April']) else None,
                    'may': row['May'] if pandas.notna(row['May']) else None,
                    'jun': row['June'] if pandas.notna(row['June']) else None,
                    'jul': row['July'] if pandas.notna(row['July']) else None,
                    'aug': row['August'] if pandas.notna(row['August']) else None,
                    'sep': row['September'] if pandas.notna(row['September']) else None,
                    'oct': row['October'] if pandas.notna(row['October']) else None,
                    'nov': row['November'] if pandas.notna(row['November']) else None,
                    'dec': row['December'] if pandas.notna(row['December']) else None
                })
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return all_data, station_data

# Calculate Average Temperature For Each Season.
def calculate_seasonal_averages(all_data):
    seasonal_temps = {
        'Summer': [],
        'Autumn': [],
        'Winter': [],
        'Spring': []
    }
    
    for record in all_data:
        summer_temps = [record['dec'], record['jan'], record['feb']]
        summer_temps = [t for t in summer_temps if t is not None]
        if summer_temps:
            seasonal_temps['Summer'].extend(summer_temps)
        
        autumn_temps = [record['mar'], record['apr'], record['may']]
        autumn_temps = [t for t in autumn_temps if t is not None]
        if autumn_temps:
            seasonal_temps['Autumn'].extend(autumn_temps)
        
        winter_temps = [record['jun'], record['jul'], record['aug']]
        winter_temps = [t for t in winter_temps if t is not None]
        if winter_temps:
            seasonal_temps['Winter'].extend(winter_temps)
        
        spring_temps = [record['sep'], record['oct'], record['nov']]
        spring_temps = [t for t in spring_temps if t is not None]
        if spring_temps:
            seasonal_temps['Spring'].extend(spring_temps)
    
    # Seasonal Average Calculation
    seasonal_averages = {}
    for season, temps in seasonal_temps.items():
        if temps:
            seasonal_averages[season] = numpy.mean(temps)
        else:
            seasonal_averages[season] = 0.0    
    return seasonal_averages

# Finding Station With Largest Temperature.
def find_largest_temperature_range(station_data):
    station_ranges = {}

    for station, temps in station_data.items():
        if temps:
            max_temp = max(temps)
            min_temp = min(temps)
            temp_range = max_temp - min_temp
            station_ranges[station] = {
                'range': temp_range,
                'max': max_temp,
                'min': min_temp
            }
    
    if not station_ranges:
        return []
    
    # Finding The Maximum Range
    max_range = max(station_ranges.values(), key=lambda x: x['range'])['range']
    
    # Finding Stations With This Maximum Range
    max_range_stations = [
        (station, data) for station, data in station_ranges.items() 
        if data['range'] == max_range
    ]
    
    return max_range_stations
# Finding Stations With Most Stable Temperature
def find_temperature_stability(station_data):
    station_std_devs = {}
    
    for station, temps in station_data.items():
        if len(temps) > 1:
            std_dev = numpy.std(temps)
            station_std_devs[station] = std_dev
    
    if not station_std_devs:
        return [], []
    
    min_std_dev = min(station_std_devs.values())
    most_stable = [
        (station, std_dev) for station, std_dev in station_std_devs.items() 
        if std_dev == min_std_dev
    ]
    
    max_std_dev = max(station_std_devs.values())
    most_variable = [
        (station, std_dev) for station, std_dev in station_std_devs.items() 
        if std_dev == max_std_dev
    ]
    
    return most_stable, most_variable

#Saving Results to TXT Files
def save_results(seasonal_averages, max_range_stations, most_stable, most_variable):

    # Seasonal Averages
    with open('average_temp.txt', 'w') as f:
        for season, avg_temp in seasonal_averages.items():
            f.write(f"{season}: {avg_temp:.1f}°C\n")
    
    # Largest Temperature Range
    with open('largest_temp_range_station.txt', 'w') as f:
        if max_range_stations:
            for station, data in max_range_stations:
                f.write(f"Station {station}: Range {data['range']:.1f}°C (Max: {data['max']:.1f}°C, Min: {data['min']:.1f}°C)\n")
        else:
            f.write("No data available\n")
    
    # Temperature Stability
    with open('temperature_stability_stations.txt', 'w') as f:
        if most_stable:
            f.write("Most Stable: ")
            stable_stations = [f"Station {station}: StdDev {std_dev:.1f}°C" for station, std_dev in most_stable]
            f.write(", ".join(stable_stations) + "\n")
        else:
            f.write("Most Stable: No data available\n")
        
        if most_variable:
            f.write("Most Variable: ")
            variable_stations = [f"Station {station}: StdDev {std_dev:.1f}°C" for station, std_dev in most_variable]
            f.write(", ".join(variable_stations) + "\n")
        else:
            f.write("Most Variable: No data available\n")

def main():

    print("Starting Temperature Data Analysis...")
    print("=" * 50)
    
    temperatures_folder = "temperatures"
    all_data, station_data = load_temperature_data(temperatures_folder)
    
    if not all_data:
        print("No data found! Please check the temperatures folder.")
        return
    
    print(f"\nLoaded data from {len(all_data)} station-year records")
    print(f"Found {len(station_data)} unique stations")
    
    print("\nCalculating seasonal averages...")
    seasonal_averages = calculate_seasonal_averages(all_data)
    
    print("Finding station with largest temperature range...")
    max_range_stations = find_largest_temperature_range(station_data)
    
    print("Analyzing temperature stability...")
    most_stable, most_variable = find_temperature_stability(station_data)
    
    print("\nSaving results...")
    save_results(seasonal_averages, max_range_stations, most_stable, most_variable)
    
    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)
    
    print("\nSeasonal Averages:")
    for season, avg_temp in seasonal_averages.items():
        print(f"  {season}: {avg_temp:.1f}°C")
    
    print(f"\nLargest Temperature Range:")
    if max_range_stations:
        for station, data in max_range_stations:
            print(f"  Station {station}: Range {data['range']:.1f}°C (Max: {data['max']:.1f}°C, Min: {data['min']:.1f}°C)")
    
    print(f"\nTemperature Stability:")
    if most_stable:
        stable_stations = [f"Station {station}: StdDev {std_dev:.1f}°C" for station, std_dev in most_stable]
        print(f"  Most Stable: {', '.join(stable_stations)}")
    
    if most_variable:
        variable_stations = [f"Station {station}: StdDev {std_dev:.1f}°C" for station, std_dev in most_variable]
        print(f"  Most Variable: {', '.join(variable_stations)}")
    
    print(f"\nResults saved to:")
    print(f"  - average_temp.txt")
    print(f"  - largest_temp_range_station.txt")
    print(f"  - temperature_stability_stations.txt")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
