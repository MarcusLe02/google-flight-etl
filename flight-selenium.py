from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import pandas as pd
import datetime
import time


def scrape(departure_city, arrival_city, date_leave, date_return, max_retries=3):
    retries = 0

    while retries < max_retries:
        web = f"https://www.google.com/travel/flights?q=Flights%20to%20{arrival_city}%20from%20{departure_city}%20on%20{date_leave}%20through%20{date_return}"
        driver = webdriver.Chrome()
        driver.get(web)
        driver.maximize_window()

        # Lists to hold all flight data
        all_departure_times = []
        all_arrival_times = []
        all_companies = []
        all_prices = []

        flight_entries = driver.find_elements(By.CSS_SELECTOR, 'div.yR1fYc')

        for entry in flight_entries:
            try:
                departure_time = entry.find_element(By.CSS_SELECTOR, "span[aria-label^='Departure time:']").text
                departure_time = convert_time(departure_time)
                all_departure_times.append(departure_time)

                arrival_time = entry.find_element(By.CSS_SELECTOR, "span[aria-label^='Arrival time:']").text
                arrival_time = convert_time(arrival_time)
                all_arrival_times.append(arrival_time)

                company = entry.find_element(By.CSS_SELECTOR, '.sSHqwe.tPgKwe.ogfYpf > span').text
                all_companies.append(company)

                price = entry.find_element(By.CSS_SELECTOR, '.YMlIz.FpEdX > span').text
                if price == 'Price unavailable':
                    price = ' N/A'
                all_prices.append(price[1:])
            except Exception as e:
                print(f"Exception: {e}")
                continue

        driver.quit()

        if all_departure_times:
            # Create a DataFrame from the collected flight data
            flights_df = pd.DataFrame({
                'Departure City': [departure_city] * len(all_departure_times),
                'Arrival City': [arrival_city] * len(all_departure_times),
                'Date Leave': [date_leave] * len(all_departure_times),
                'Date Return': [date_return] * len(all_departure_times),
                'Departure Time': all_departure_times,
                'Arrival Time': all_arrival_times,
                'Company': all_companies,
                'Price': all_prices
            })
            print(f'Finish scraping for {departure_city},{arrival_city},{date_leave},{date_return}')
            return flights_df
        else:
            print(f'Retrying scraping for {departure_city},{arrival_city},{date_leave},{date_return}')
            retries += 1
            # Sleep for a few seconds before retrying
            time.sleep(2)

    print(f'Max retries reached for {departure_city},{arrival_city},{date_leave},{date_return}')
    return None  # Return None if max retries are reached without success


def convert_time(time_str):
    if "+1" in time_str:
        time_str = time_str[:-2]
    # Check if the time_str contains "AM"
    if "AM" in time_str:
        # Remove "AM" and return the time as is
        return time_str.replace("AM", "").strip()
    elif "PM" in time_str:
        # Remove "PM" and split the time into hours and minutes
        time_parts = time_str.replace("PM", "").strip().split(":")
        if len(time_parts) == 2:
            # Convert the hour part to an integer and add 12 to it
            hour = int(time_parts[0]) + 12
            # Ensure the hour is in 24-hour format (0-23)
            hour %= 24
            # Construct and return the modified time string
            return f"{hour:02d}:{time_parts[1]}"
    
    # If "AM" or "PM" is not found, return the time as is
    return time_str

# Create an empty list to store the results of each scrape
results = []

# Define the date combinations you want to scrape
date_combinations = [
    ('2024-02-05', '2024-02-16'),
    ('2024-02-05', '2024-02-17'),
    ('2024-02-05', '2024-02-18'),
    ('2024-02-06', '2024-02-16'),
    ('2024-02-06', '2024-02-17'),
    ('2024-02-06', '2024-02-18'),
    ('2024-02-07', '2024-02-16'),
    ('2024-02-07', '2024-02-17'),
    ('2024-02-07', '2024-02-18')
]

# Perform the scrapes and store the results in the list
for date_leave, date_return in date_combinations:
    result = scrape('HCM', 'HAN', date_leave, date_return)
    results.append(result)

# Concatenate all the results into a single DataFrame
final_df = pd.concat(results, ignore_index=True)

# Add the current date to the file name
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
file_name = f"/Users/marcusle02/Documents/Learning/google_flight_etl/RT Flight Data/flight_data_{current_date}.csv"

# Save the concatenated file as a CSV file
final_df.to_csv(file_name, index=False, encoding='utf-8')

print(f"Data saved to {file_name}")