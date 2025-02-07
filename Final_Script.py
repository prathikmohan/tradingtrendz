#!pip install pytz
#!pip install requests
import sys
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
import os
import glob

######################################## GENERATING BASE AND DATA SAVING PATHS ####################

# Get the directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # Store all CSVs inside a 'data' folder

# Ensure the data folder exists
os.makedirs(DATA_DIR, exist_ok=True)





######################################## GENERATING .CSV FILES ####################################

#-------------CHECK IF WEEKEND OR WEEKDAY, IF WEEKEND JUST PRINT TODAY'S TIME, ELSE EXECUTE CODE (PUT INSIDE IT) AND THEN PRINT TIME----------------

# Function to check if today is a weekend
def is_weekend():
    # Get the current time in IST
    today = datetime.now(pytz.timezone('Asia/Kolkata'))
    return today.weekday() >= 5  # 5 is Saturday, 6 is Sunday

# Get the current time and day in IST
today = datetime.now(pytz.timezone('Asia/Kolkata'))
current_time = today.strftime("%H:%M")
current_day = today.strftime("%A")  # Get the full name of the day (e.g., Monday)

# Check if today is a weekend
if is_weekend():
    print(f"Last Updated on: {current_time} IST, {current_day}")
    #sys.exit()  # Exiting the program
else:
        # -------------------DOWNLOAD THE DATA---------------------

    # URL to download the CSV file
    csv_url = 'https://www.nseindia.com/api/etf?csv=true&selectValFormat=crores'

    # Create a session to persist certain parameters across requests
    session = requests.Session()

    # Set headers to mimic a browser visit
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.nseindia.com/',
        'X-Requested-With': 'XMLHttpRequest',  # Sometimes required for AJAX requests
    }

    # Send a request to the NSE homepage to get cookies
    session.get('https://www.nseindia.com', headers=headers)

    # Download the CSV file
    csv_response = session.get(csv_url, headers=headers)

    # Download ETF .csv from https://www.nseindia.com/market-data/exchange-traded-funds-etf

    # Check if the CSV download was successful
    if csv_response.status_code == 200:
        #file_path = 'C:/Users/prathikm/Desktop/data_wrapper/etf_data.csv'
        file_path = os.path.join(DATA_DIR,"etf_data.csv")

        # Save the CSV file
        with open(file_path, 'wb') as f:
            f.write(csv_response.content)
        print("CSV file downloaded successfully.")
    else:
        print(f"Failed to download the CSV file. Status code: {csv_response.status_code}")

    # Continue with the rest of your program | INSERT YOUR ACTUAL PROGRAM TO GENERATE THE .CSV HERE
    print(f"Last Updated on: {current_time} IST, {current_day}")

    time.sleep(30)

        # -------------------ANALYZE THE DATA---------------------

        # Read the CSV file into a DataFrame
    #df = pd.read_csv('C:/Users/prathikm/Desktop/data_wrapper/etf_data.csv')
    df = pd.read_csv(os.path.join(DATA_DIR,"etf_data.csv"))

        # First, strip whitespace from column names. Here it is \n in .csv
    df.columns = df.columns.str.strip()

        # Convert SYMBOL column to string
    df['SYMBOL'] = df['SYMBOL'].astype(str)

        # Remove comma in between numbers and then convert VOLUME column to integer
        #df['VOLUME'] = df['VOLUME'].str.replace(',', '', regex=False).astype(int)
    df['VOLUME'] = df['VOLUME'].str.replace(',', '', regex=False).str.replace('-', '0', regex=False).astype(int)

        # Now you can select the columns
    selected_columns = df[['SYMBOL', 'VOLUME']]

        # Sort the data frame as per descending VOLUME
    sorted_columns = selected_columns.sort_values(by='VOLUME', ascending=False)

        # Calculate the Total volume (needed to get the % of asset class in the end) ||||| **** total_volume ****
    total_volume = df['VOLUME'].sum()

        # Filter for rows with VOLUME only greater than 0L
    filtered_columns = sorted_columns[sorted_columns['VOLUME'] > 0]

        # Reset the index by dropping the old index/ dont convert the old index to a new column
    filtered_columns_reset = filtered_columns.reset_index(drop=True)
    filtered_columns_reset.index += 1

        #print(f"Total Volume: {total_volume}")

        #filtered_columns_reset

        # Finally, we have volume > 20L filtered in descending order with proper index and also total_volume to calculate the % asset of each class in the end.
        # Next we need to make a df with asset classes of similar types-give it one name, and replace the same classes in our df here with one name from that file.

        # -------------------MATCH AND REPLACE---------------------

        # Load the input CSV file
    #csv_file_path = 'C:/Users/prathikm/Desktop/data_wrapper/Replace_Symbols_Updated.csv'  # Replace with your actual CSV file path
    csv_file_path = os.path.join(DATA_DIR,"Replace_Symbols_Updated.csv")
    csv_df = pd.read_csv(csv_file_path)

        # Iterate using the actual index values of the DataFrame
    for index in filtered_columns_reset.index:  # Use the DataFrame's index
        symbol = filtered_columns_reset.at[index, 'SYMBOL']  # Get the SYMBOL value
            # Search for the symbol in the CSV DataFrame (from row 2 onwards)
        for col in csv_df.columns:
                # Check if the symbol exists in the column (starting from row 2)
            if symbol in csv_df[col].values:
                    # Replace SYMBOL name in the sheet with the column header (row 1)
                filtered_columns_reset.at[index, 'SYMBOL'] = col  # Use the column name directly
                break  # Break after the first match


        # Display the updated sheet DataFrame
        #print(filtered_columns_reset)

        # -------------------COMBINE AND ADD THE VOLUMES, THEN SORT---------------------

    combined_df = filtered_columns_reset.groupby('SYMBOL', as_index=False)['VOLUME'].sum()

    combined_df = combined_df.sort_values(by='VOLUME', ascending=False)
    combined_df_reset = combined_df.reset_index(drop=True)
    combined_df_reset.index += 1

        # -------------------GET VALUE OF LIQUID FUNDS---------------------

        # Check if 'Liquid Funds' exists and get the value
    if not combined_df_reset.loc[combined_df_reset['SYMBOL'] == 'Liquid Funds', 'VOLUME'].empty:
        liquid_funds_value = combined_df_reset.loc[combined_df_reset['SYMBOL'] == 'Liquid Funds', 'VOLUME'].values[0]
    else:
        liquid_funds_value = None  # or some default value

    print("\nVolume of 'Liquid Funds':", liquid_funds_value)

        # Check if liquid_funds_value is an integer
    if liquid_funds_value is not None:

        percentage_liquid_funds = (liquid_funds_value / total_volume) * 100

            # Print the result formatted to 2 decimal places
        print(f"\nPercentage Volume of 'Liquid Funds': {percentage_liquid_funds:.2f}%")
    else:
        print("\nError Calculating 'Liquid Funds' volume, we are looking into this issue!")

        # -----------WRITE LIQUID FUNDS VALUE IN A .CSV ----------------

        # Create a small DataFrame with one row
    df_overwrite = pd.DataFrame({
        "LiquidFundsVolume": [liquid_funds_value],
        "LiquidFundsPercentage": [f"{percentage_liquid_funds:.2f}%"]
    })

        # Specify the path to your CSV
    #output_csv = r"C:/Users/prathikm/Desktop/data_wrapper/liquid_funds_stats.csv"
    output_csv = os.path.join(DATA_DIR,"liquid_funds_stats.csv")

        # Overwrite the file each time
    df_overwrite.to_csv(output_csv, index=False, header=True)


        # -------------------REMOVE LIQUID FUNDS---------------------

    combined_df_reset = combined_df_reset.drop(combined_df_reset[combined_df_reset['SYMBOL'] == 'Liquid Funds'].index)

        # -------------------CALCULATE THE % OF EACH ASSET/SECTOR CLASS---------------------

        # Calculate percentage for each symbol
    combined_df_reset['PERCENTAGE'] = (combined_df_reset['VOLUME'] / total_volume) * 100

    combined_df_reset['PERCENTAGE'] = combined_df_reset['PERCENTAGE'].round(2)

    combined_df_reset

        # -------------------EXPORT TO .CSV---------------------

        #combined_df_reset["PERCENTAGE"] = combined_df_reset["PERCENTAGE"].astype(str) + '%'

        #combined_df_reset.to_csv("etf_nov_30.csv", index=False)

        #combined_df_reset.to_csv("/content/drive/MyDrive/TradingTrendz/04_12_2024.csv", index=False)

        # -------------------EXPORT TO .CSV AS TODAYSDAY_WEEKNUMBER---------------------

        # combined_df_reset is our DataFrame

        # Get today's date
    today = datetime.now()

        # Get the day of the week (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
    day_of_week = today.strftime('%A')  # Full name of the day
    week_number = today.isocalendar()[1]  # ISO week number

        # Create a filename based on the day and week number
    filename = f"{day_of_week}_Week{week_number}.csv"

    file_path = os.path.join(DATA_DIR, filename)
        # Save the DataFrame to CSV
    #combined_df_reset.to_csv(f"C:/Users/prathikm/Desktop/data_wrapper/{filename}", index=False)
    combined_df_reset.to_csv(file_path, index=False)

    print(f"File saved as: {file_path}")

    time.sleep(30)

                # -------------------UPDATE THE LATEST .CSV BY COMPARING THE VOLUME AND ADDING NEW COLUMN % Change From Yesterday---------------------



        # Load the newly generated CSV file
    today = datetime.now()
    day_of_week = today.strftime('%A')
    week_number = today.isocalendar()[1]
    new_filename = f"{day_of_week}_Week{week_number}.csv"
    #new_file_path = f"C:/Users/prathikm/Desktop/data_wrapper/{new_filename}"
    new_file_path = os.path.join(DATA_DIR, new_filename)

        # Calculate yesterday's date
    yesterday = today - timedelta(days=1)
    yesterday_day_of_week = yesterday.strftime('%A')
    yesterday_week_number = yesterday.isocalendar()[1]
    yesterday_filename = f"{yesterday_day_of_week}_Week{yesterday_week_number}.csv"
    #yesterday_file_path = f"C:/Users/prathikm/Desktop/data_wrapper/{yesterday_filename}"
    yesterday_file_path = os.path.join(DATA_DIR, yesterday_filename)

        # Check if yesterday's file exists
    if os.path.exists(yesterday_file_path):
            # Load both CSV files
        new_df = pd.read_csv(new_file_path)
        yesterday_df = pd.read_csv(yesterday_file_path)

            # Merge DataFrames on the SYMBOL column
        merged_df = pd.merge(new_df, yesterday_df[['SYMBOL', 'VOLUME']], on='SYMBOL', suffixes=('_new', '_yesterday'))

            # Calculate % Change From Yesterday
        merged_df['% Change From Yesterday'] = ((merged_df['VOLUME_new'] - merged_df['VOLUME_yesterday']) / merged_df['VOLUME_yesterday']) * 100

            # Keep the order of SYMBOL as per today's file
        updated_df = new_df.copy()
        updated_df = updated_df.merge(merged_df[['SYMBOL', '% Change From Yesterday']], on='SYMBOL', how='left')

            # Save the updated DataFrame to the same CSV file
        updated_df.to_csv(new_file_path, index=False)

        print(f"File updated: {new_filename}")

    else:
            # If it's Monday, look for last Friday's file
        if day_of_week == "Monday":
                # Calculate last Friday's date (Monday minus 3 days)
            last_friday = today - timedelta(days=3)

                # Construct last Friday’s filename and path
            last_friday_day_of_week = last_friday.strftime('%A')
            last_friday_week_number = last_friday.isocalendar()[1]
            last_friday_filename = f"{last_friday_day_of_week}_Week{last_friday_week_number}.csv"
            #last_friday_file_path = f"C:/Users/prathikm/Desktop/data_wrapper/{last_friday_filename}"
            last_friday_file_path = os.path.join(DATA_DIR, last_friday_filename)

                # Check if that file exists
            if os.path.exists(last_friday_file_path):
                print(f"Yesterday's file does not exist (Sunday). Today is Monday. Using last Friday's file: {last_friday_filename}")

                    # (Optional) Repeat your merge/update logic using last Friday's file
                new_df = pd.read_csv(new_file_path)
                friday_df = pd.read_csv(last_friday_file_path)

                    # Merge DataFrames on 'SYMBOL'
                merged_df = pd.merge(
                    new_df,
                    friday_df[['SYMBOL', 'VOLUME']],
                    on='SYMBOL',
                    suffixes=('_new', '_friday')
                )

                    # Calculate % Change From Friday
                merged_df['% Change From Yesterday'] = (
                    (merged_df['VOLUME_new'] - merged_df['VOLUME_friday'])
                    / merged_df['VOLUME_friday']
                ) * 100

                    # Keep today's order of SYMBOL
                updated_df = new_df.merge(
                    merged_df[['SYMBOL', '% Change From Yesterday']],
                    on='SYMBOL',
                    how='left'
                )

                    # Save the updated file
                updated_df.to_csv(new_file_path, index=False)
                print(f"File updated using last Friday's file: {last_friday_filename}")

            else:
                print(f"Last Friday's file '{last_friday_filename}' does not exist. Cannot update today's file.")

        else:
                # For Tuesday–Friday, if the "yesterday" file doesn’t exist,
                # simply note it (or handle however you prefer).
            print(f"Yesterday's file {yesterday_file_path} does not exist. No update performed.")


        # else:
        #     # If it is Monday, we look for last Friday's file
        #     if day_of_week == "Monday":
        #       # Calculate last Friday's date (Monday minus 3 days)
        #         last_friday = today - timedelta(days=3)
        #         # Construct last Friday’s filename and path
        #         last_friday_day_of_week = last_friday.strftime('%A')
        #         last_friday_week_number = last_friday.isocalendar()[1]
        #         last_friday_filename = f"{last_friday_day_of_week}_Week{last_friday_week_number}.csv"
        #         last_friday_file_path = f"/content/drive/MyDrive/TradingTrendz/{last_friday_filename}"

        #   # WRITE LOGIC HERE THAT IF TODAY IS MONDAY THEN PICK FRIDAY'S FILE (last week nos.). FOR SAT AND SUNDAY WILL NEVER RUN ONLY IN THE FIRST LOOP.
        #   # - SO ONLY DAY THAT WILL RUN IS MONDAY.
        #     print(f"Yesterday's file {yesterday_file_path} does not exist. So today is Monday, hence picking Friday's File.")

time.sleep(30)

######################################## HTML GENERATION FROM HERE ################################

# Just to print updated time and day for the website
def get_last_updated_string():
    """Return a string like 'Last Updated on: HH:MM IST, Monday' in IST."""
    now_ist = datetime.now(pytz.timezone('Asia/Kolkata'))
    current_time = now_ist.strftime("%H:%M")
    current_day = now_ist.strftime("%A")
    return f"Last Updated on: {current_time} IST, {current_day}"

def get_latest_csv(directory):
    """
    Returns the full path to the most recently created/modified CSV file
    in `directory` that matches '*_Week*.csv'.
    If no such file exists, returns None.
    """
    pattern = os.path.join(directory, "*_Week*.csv")
    files = glob.glob(pattern)

    if not files:
        return None  # No matching CSV found

    # Pick the file with the greatest creation time (ctime).
    latest_file = max(files, key=os.path.getctime)
    return latest_file


def main():
    # ===============================
    # 1) Read your CSV into a DataFrame
    # ===============================
    
    #folder_path = r"C:/Users/prathikm/Desktop/data_wrapper"
    folder_path = DATA_DIR
    csv_path = get_latest_csv(folder_path)

    if csv_path is None:
        print("No CSV matching '*_Week*.csv' found in:", folder_path)
        return

    print("Using latest CSV:", csv_path)

    # Now read it with pandas (assuming it has the same columns as your earlier code)
    import pandas as pd
    df = pd.read_csv(csv_path)
    # Proceed with your logic here...
    # e.g. style the DataFrame, generate HTML, etc.
    
    #csv_path = r"C:/Users/prathikm/Desktop/data_wrapper/Monday_Week5.csv"
    #df = pd.read_csv(csv_path)

    # Rename columns if needed. Must match the actual CSV columns:
    # [ "Symbol", "Volume", "Percentage of Total Vol.", "Change from Yesterday" ]
    df.columns = ["Symbol", "Volume", "Percentage of Total Vol.", "Change from Yesterday"]

    # Convert numeric columns
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")
    df["Percentage of Total Vol."] = pd.to_numeric(df["Percentage of Total Vol."], errors="coerce")
    df["Change from Yesterday"] = pd.to_numeric(df["Change from Yesterday"], errors="coerce")

    # ===============================
    # 2) Create a styled DataFrame
    # ===============================

    # Helper: color positive (green) / negative (red)
    def color_pos_neg(val):
        if pd.isna(val):
            return ""
        return "color: #009879" if val > 0 else "color: #d13535"

    # Custom format for numeric columns with a "%" suffix (no extra *100)
    def pct_format(x):
        if pd.isna(x):
            return ""
        return f"{x:.2f}%"

    # Build the style pipeline:
    #
    # Note: We clamp the heatmap's vmax=50 so anything above 50% gets
    # the same darkest color.
    styled_df = (
        df.style
          .format({
              "Percentage of Total Vol.": pct_format,
              "Change from Yesterday": pct_format
          })
          .bar(subset=["Volume"], color="#F1AB00", vmin=0)
          .background_gradient(
              subset=["Percentage of Total Vol."],
              cmap="GnBu", 
              vmin=0,
              vmax=50  # saturate color at 50
          )
          .map(color_pos_neg, subset=["Change from Yesterday"])
    )

    # Convert styled table to HTML
    table_html = styled_df.to_html()

    # ===============================
    # 3) Read liquid_funds_stats.csv to get LiquidFundsVolume & LiquidFundsPercentage
    # ===============================
    #liquid_csv = r"C:/Users/prathikm/Desktop/data_wrapper/liquid_funds_stats.csv"  # <-- adjust to your actual file path
    liquid_csv = os.path.join(DATA_DIR,"liquid_funds_stats.csv")
    try:
        df_liquid = pd.read_csv(liquid_csv)
        # We'll assume there's only one row with columns: LiquidFundsVolume, LiquidFundsPercentage
        lf_volume = df_liquid.loc[0, "LiquidFundsVolume"]
        lf_percentage = df_liquid.loc[0, "LiquidFundsPercentage"]
        # Prepare an HTML snippet
        # Replace (Latest) with e.g. (Last Updated on: 10:31 IST, Monday)
        updated_str = get_last_updated_string()
        liquid_info_html = f"""
            <h3><span style="font-weight: normal;">{updated_str}</span></h3>
            <p><strong>Liquid Funds Volume:</strong> {lf_volume}</p>
            <p><strong>Percentage of Total ETF Volume (Liquid Funds):</strong> {lf_percentage}</p>
        """
    except Exception as e:
        print("Error reading liquid_funds_stats.csv:", e)
        # Fallback text if the file is missing or can't be read
        updated_str = get_last_updated_string()
        liquid_info_html = """
            <h3><span style="font-weight: normal;">{updated_str}</span></h3>
            <p style="color:red;">
                Liquid Funds data unavailable. (Could not read liquid_funds_stats.csv)
            </p>
        """

    # ===============================
    # 3) HOME/INDEX PAGE HTML
    # ===============================
    home_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>ETF Volume Analysis</title>
    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
        }}

        /* Left ad column */
        #left-ad {{
            position: fixed;
            left: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-right: 1px solid #ccc;
            padding: 10px;
        }}

        /* Right ad column */
        #right-ad {{
            position: fixed;
            right: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-left: 1px solid #ccc;
            padding: 10px;
        }}

        /* Main content area (center) */
        #main-content {{
            margin: 0 180px;  /* leaves space for side ads */
            padding: 20px;
        }}

        /* Navigation bar or top links */
        .top-nav {{
            margin-bottom: 20px;
        }}
        .top-nav a {{
            margin-right: 15px;
            text-decoration: none;
            color: #0073aa;
            font-weight: bold;
        }}
        .top-nav a:hover {{
            text-decoration: underline;
        }}

        /* Bottom ad area */
        #bottom-ad {{
            background: #f8f8f8;
            border-top: 1px solid #ccc;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }}

        /* Scrollable table container so user doesn't need to zoom out */
        .table-container {{
            width: 100%;
            overflow-x: auto;  /* horizontal scroll if table is too wide */
            margin-top: 20px;
        }}

        /* Basic table styling (pandas sets inline styles for bars/colors) */
        table {{
            border-collapse: collapse;
            margin: 0 auto;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
            white-space: nowrap;
        }}
    </style>

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-60WBWC80X3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-60WBWC80X3');
    </script>

</head>

<body>
    <!-- Left Ad Placeholder -->
    <div id="left-ad">
        <!-- Replace with your AdSense (or other) code -->
        <h4>Left Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Right Ad Placeholder -->
    <div id="right-ad">
        <!-- Replace with your AdSense code -->
        <h4>Right Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Main Content -->
    <div id="main-content">
        <!-- Simple nav links (Home, About) -->
        <div class="top-nav">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="privacy.html">Privacy</a>
            <a href="terms.html">Terms</a>
            <a href="disclaimer.html">Disclaimer</a>
            <a href="cookie.html">Cookie Policy</a>
            <a href="donate.html">Donate</a>
        </div>

        <h1>ETF Volume Analysis</h1>
        <p>
          The table below shows the approximate traded Volume of ETFs in the Indian Stock Market.
          It is updated on a daily basis and can be accessed for free without signup.
        </p>

        <!-- Liquid Funds Info from the second CSV (liquid_funds_stats.csv) -->
        <div style="background-color:#f4f4f4; padding:10px; margin-bottom:20px;">
          {liquid_info_html}
        </div>

        <div class="table-container">
          {table_html}
        </div>

        <p style="font-size: 0.9em; color: #666;">
          *All data is analyzed by tradingtrendz.in. I am not SEBI registered, and the above analysis 
          is not a recommendation to buy or sell any asset. Please read the disclaimer section of 
          my website. Special trading sessions and weekends will be ignored from analysis.
        </p>
    </div>

    <!-- Bottom Ad Placeholder -->
    <div id="bottom-ad">
        <!-- Replace with your AdSense code -->
        <h4>Bottom Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>
</body>
</html>
"""

    # ===============================
    # 4) ABOUT PAGE HTML
    # ===============================
    about_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>About tradingtrendz.in</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        /* Left ad column */
        #left-ad {
            position: fixed;
            left: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-right: 1px solid #ccc;
            padding: 10px;
        }

        /* Right ad column */
        #right-ad {
            position: fixed;
            right: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-left: 1px solid #ccc;
            padding: 10px;
        }

        /* Main content area (center) */
        #main-content {
            margin: 0 180px;  /* leaves space for side ads */
            padding: 20px;
        }

        /* Navigation bar or top links */
        .top-nav {
            margin-bottom: 20px;
        }
        .top-nav a {
            margin-right: 15px;
            text-decoration: none;
            color: #0073aa;
            font-weight: bold;
        }
        .top-nav a:hover {
            text-decoration: underline;
        }

        /* Bottom ad area */
        #bottom-ad {
            background: #f8f8f8;
            border-top: 1px solid #ccc;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }
    </style>


    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-60WBWC80X3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-60WBWC80X3');
    </script>

</head>
<body>
    <!-- Left Ad Placeholder -->
    <div id="left-ad">
        <!-- Replace with your AdSense (or other) code -->
        <h4>Left Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Right Ad Placeholder -->
    <div id="right-ad">
        <!-- Replace with your AdSense code -->
        <h4>Right Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <div id="main-content">
        <!-- Simple nav links (Home, About) -->
        <div class="top-nav">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="privacy.html">Privacy</a>
            <a href="terms.html">Terms</a>
            <a href="disclaimer.html">Disclaimer</a>
            <a href="cookie.html">Cookie Policy</a>
            <a href="donate.html">Donate</a>
        </div>

        <h1>About tradingtrendz.in</h1>
        
        <!-- Your image here. Adjust src, alt, and style as needed. -->
        <img src="IMG152632.jpg" alt="Photo of John Jacob" style="max-width:200px; border-radius: 50%; margin-bottom: 20px;">

        
        <p>
            Hello! My name is Prathik. I’m an engineering professional and currently also pursuing my M.Sc. in Data Science 
            and AI. As a side hobby, I engage in positional trading and occasionally scalp the markets in my free hours. 
            Over time, I developed my own algorithms using statistics, and I've found them to be quite successful 
            in generating profits.
        </p>
        <p>
            I strongly believe in the potential of ETFs/Exchange Traded Funds, both for investing and 
            trading purposes. Through my personal experience, I’ve noticed that the volume of traded ETFs 
            can sometimes give a sense of market momentum or direction. For instance, I once observed 
            unusually high volume in a China ETF on a Monday, and the same pattern continued for the next 
            few days—after which the underlying index went up, essentially validating our volume-based 
            observation. I have seen this kind of volume-based pattern occur many times in other ETFs as well.
        </p>
        <p>
            Of course, I’m not suggesting that mere volume analysis alone is enough to predict the market. 
            It’s more like an additional tool in our toolbox—one that can give us early signals or guidance 
            when combined with other trading strategies. 
        </p>
        <p>
            That’s why I created <strong>tradingtrendz.in</strong>. Behind the scenes, I aggregate ETF volume 
            data and update it regularly. I personally check the site every day to see which ETFs are trending 
            and where volume is surging. The website's backend code runs over 1,600+ lines. One notable exclusion from my table is liquid funds, as their volume 
            often spikes on Fridays or weekends (due to people parking money in them), which can distort 
            the overall volume analysis when compared to equity‑based or sectoral ETFs.
        </p>
        <p>
            Going forward, as new ETFs are launched by AMCs, they will need to be updated and grouped into specific
            sectors or categories in our table. I will update this whenever I get free time, though it may not
            happen immediately—but rest assured, I will keep an eye on it. Until then, the newly launched ETF
            will be listed somewhere below in the table, so please excuse any temporary placement. My main advice
            on how to use this site is simple: observe the consistent or rising volumes over multiple days to get a 
            sense of which sectors might be gaining market attention. If a particular sector's ETF volume stays
            high consistently, that might indicate a trend worth exploring.
        </p>
        <p>
            Always remember: do your own thorough research and testing. Volume trends can be a helpful signal, 
            but they’re never a magic bullet. I wish you all the best in your trading and investing journey!
        </p>
    </div>

    <!-- Bottom Ad Placeholder -->
    <div id="bottom-ad">
        <!-- Replace with your AdSense code -->
        <h4>Bottom Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>
</body>
</html>
"""


    # ===============================
    # 5) CONTACT PAGE HTML
    # ===============================
    contact_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Contact Us</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        /* Left ad column */
        #left-ad {
            position: fixed;
            left: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-right: 1px solid #ccc;
            padding: 10px;
        }

        /* Right ad column */
        #right-ad {
            position: fixed;
            right: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-left: 1px solid #ccc;
            padding: 10px;
        }

        /* Main content area (center) */
        #main-content {
            margin: 0 180px;  /* leaves space for side ads */
            padding: 20px;
        }

        /* Navigation bar or top links */
        .top-nav {
            margin-bottom: 20px;
        }
        .top-nav a {
            margin-right: 15px;
            text-decoration: none;
            color: #0073aa;
            font-weight: bold;
        }
        .top-nav a:hover {
            text-decoration: underline;
        }

        /* Bottom ad area */
        #bottom-ad {
            background: #f8f8f8;
            border-top: 1px solid #ccc;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }

        .contact-section {
            max-width: 800px;
        }
    </style>


    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-60WBWC80X3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-60WBWC80X3');
    </script>


</head>
<body>
    <!-- Left Ad Placeholder -->
    <div id="left-ad">
        <!-- Replace with your AdSense (or other) code -->
        <h4>Left Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Right Ad Placeholder -->
    <div id="right-ad">
        <!-- Replace with your AdSense code -->
        <h4>Right Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <div id="main-content">
        <!-- Simple nav links (Home, About) -->
        <div class="top-nav">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="privacy.html">Privacy</a>
            <a href="terms.html">Terms</a>
            <a href="disclaimer.html">Disclaimer</a>
            <a href="cookie.html">Cookie Policy</a>
            <a href="donate.html">Donate</a>
        </div>

        <h1>Contact Us</h1>
        <div class="contact-section">
        <p>
            If you have any questions, feedback, or are interested in advertising, I would love to hear
            from you! Also, if you would like to purchase historical .csv data, you can use the information
            below to reach out to me.
        </p>
        <h3>Email</h3>
        <p>
            <a href="mailto:mailtothedeveloper@gmail.com">mailtothedeveloper@gmail.com</a>
        </p>
        
        <!--
        <h3>Phone</h3>
         <p>
            +91-XXXX-XXXXXX (example placeholder)
        </p>

        <h3>Social Media</h3>
        <p>
            Twitter: <a href="https://twitter.com/YourTwitter">@YourTwitter</a><br />
            LinkedIn: <a href="https://linkedin.com/">Your LinkedIn Profile</a>
        </p>
        
        If you want a contact form, you can add it below:
        <form>
            <label>Name:</label><br/>
            <input type="text" name="name"><br/><br/>
            <label>Email:</label><br/>
            <input type="email" name="email"><br/><br/>
            <label>Message:</label><br/>
            <textarea name="message"></textarea><br/><br/>
            <button type="submit">Send</button>
        </form>
        -->
    </div>

    <!-- Bottom Ad Placeholder -->
    <div id="bottom-ad">
        <!-- Replace with your AdSense code -->
        <h4>Bottom Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>
</body>
</html>
"""



    # ===============================
    # 6) PRIVACY PAGE HTML
    # ===============================
    privacy_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Privacy Policy</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        /* Left ad column */
        #left-ad {
            position: fixed;
            left: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-right: 1px solid #ccc;
            padding: 10px;
        }

        /* Right ad column */
        #right-ad {
            position: fixed;
            right: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-left: 1px solid #ccc;
            padding: 10px;
        }

        /* Main content area (center) */
        #main-content {
            margin: 0 180px;  /* leaves space for side ads */
            padding: 20px;
        }

        /* Navigation bar or top links */
        .top-nav {
            margin-bottom: 20px;
        }
        .top-nav a {
            margin-right: 15px;
            text-decoration: none;
            color: #0073aa;
            font-weight: bold;
        }
        .top-nav a:hover {
            text-decoration: underline;
        }

        /* Bottom ad area */
        #bottom-ad {
            background: #f8f8f8;
            border-top: 1px solid #ccc;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }

        .contact-section {
            max-width: 800px;
        }
    </style>

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-60WBWC80X3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-60WBWC80X3');
    </script>

</head>
<body>
    <!-- Left Ad Placeholder -->
    <div id="left-ad">
        <!-- Replace with your AdSense (or other) code -->
        <h4>Left Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Right Ad Placeholder -->
    <div id="right-ad">
        <!-- Replace with your AdSense code -->
        <h4>Right Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <div id="main-content">
        <!-- Simple nav links (Home, About) -->
        <div class="top-nav">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="privacy.html">Privacy</a>
            <a href="terms.html">Terms</a>
            <a href="disclaimer.html">Disclaimer</a>
            <a href="cookie.html">Cookie Policy</a>
            <a href="donate.html">Donate</a>
        </div>

        <h1>Privacy Policy</h1>
        <div class="policy-section">
        <p>
            This policy outlines how this website tradingtrendz.in handles your 
            personal data.
        </p>
        <h3>Information We Collect</h3>
        <p>
            This website may collect personal information such as your name, email address, 
            or usage data to improve services.
        </p>

        <h3>Use of Collected Information</h3>
         <p>
            This collected data can be used to personalize your experience, respond to inquiries, 
            and analyze site performance.
        </p>

        <h3>Cookies</h3>
        <p>
            This website may use cookies to enhance your browsing experience. You can choose to disable 
            cookies through your browser settings.
        </p>
        </p>
            
        <h3>Third-Party Services</h3>
        <p>
            This website may employ third-party companies for analytics or advertising. These companies 
            have their own privacy policies regarding how they use your data.
        </p>
        
        <h3>Changes to This Policy</h3>
        <p>
            I may update this Privacy Policy from time to time. I encourage you to review it 
            periodically for any changes.
        </p>

        <!-- If you want a contact form, you can add it below:
        <form>
            <label>Name:</label><br/>
            <input type="text" name="name"><br/><br/>
            <label>Email:</label><br/>
            <input type="email" name="email"><br/><br/>
            <label>Message:</label><br/>
            <textarea name="message"></textarea><br/><br/>
            <button type="submit">Send</button>
        </form>
        -->
    </div>

    <!-- Bottom Ad Placeholder -->
    <div id="bottom-ad">
        <!-- Replace with your AdSense code -->
        <h4>Bottom Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>
</body>
</html>
"""


    # ===============================
    # 7) TERMS PAGE HTML
    # ===============================
    terms_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Terms of Service</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        /* Left ad column */
        #left-ad {
            position: fixed;
            left: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-right: 1px solid #ccc;
            padding: 10px;
        }

        /* Right ad column */
        #right-ad {
            position: fixed;
            right: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-left: 1px solid #ccc;
            padding: 10px;
        }

        /* Main content area (center) */
        #main-content {
            margin: 0 180px;  /* leaves space for side ads */
            padding: 20px;
        }

        /* Navigation bar or top links */
        .top-nav {
            margin-bottom: 20px;
        }
        .top-nav a {
            margin-right: 15px;
            text-decoration: none;
            color: #0073aa;
            font-weight: bold;
        }
        .top-nav a:hover {
            text-decoration: underline;
        }

        /* Bottom ad area */
        #bottom-ad {
            background: #f8f8f8;
            border-top: 1px solid #ccc;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }

        .contact-section {
            max-width: 800px;
        }
    </style>


    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-60WBWC80X3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-60WBWC80X3');
    </script>

</head>
<body>
    <!-- Left Ad Placeholder -->
    <div id="left-ad">
        <!-- Replace with your AdSense (or other) code -->
        <h4>Left Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Right Ad Placeholder -->
    <div id="right-ad">
        <!-- Replace with your AdSense code -->
        <h4>Right Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <div id="main-content">
        <!-- Simple nav links (Home, About) -->
        <div class="top-nav">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="privacy.html">Privacy</a>
            <a href="terms.html">Terms</a>
            <a href="disclaimer.html">Disclaimer</a>
            <a href="cookie.html">Cookie Policy</a>
            <a href="donate.html">Donate</a>
        </div>

        <h1>Terms of Service</h1>
        <div class="terms-section">
            <h3>Acceptance of Terms</h3>
            <p>
                By accessing or using tradingtrendz.in, you agree to be bound by these Terms of Service.
            </p>

            <h3>Modifications to the Service</h3>
             <p>
                tradingtrendz.in reserves the right to modify or discontinue any part of it's service at any time 
                without prior notice.
             </p>

            <h3>User Conduct</h3>
            <p>
                You agree to use this website responsibly and comply with all applicable laws. 
            </p>

            <h3>Liability</h3>
            <p>
                tradingtrendz.in is not liable for any damages arising from the use or inability 
                to use this website or any third-party links.
            </p>

            <h3>Governing Law</h3>
            <p>
                These Terms of Service are governed by the laws of India.
            </p>
        </div>    
    </div>

    <!-- Bottom Ad Placeholder -->
    <div id="bottom-ad">
        <!-- Replace with your AdSense code -->
        <h4>Bottom Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>
</body>
</html>
"""


    # ===============================
    # 8) DISCLAIMER PAGE HTML
    # ===============================
    disclaimer_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Disclaimer</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        /* Left ad column */
        #left-ad {
            position: fixed;
            left: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-right: 1px solid #ccc;
            padding: 10px;
        }

        /* Right ad column */
        #right-ad {
            position: fixed;
            right: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-left: 1px solid #ccc;
            padding: 10px;
        }

        /* Main content area (center) */
        #main-content {
            margin: 0 180px;  /* leaves space for side ads */
            padding: 20px;
        }

        /* Navigation bar or top links */
        .top-nav {
            margin-bottom: 20px;
        }
        .top-nav a {
            margin-right: 15px;
            text-decoration: none;
            color: #0073aa;
            font-weight: bold;
        }
        .top-nav a:hover {
            text-decoration: underline;
        }

        /* Bottom ad area */
        #bottom-ad {
            background: #f8f8f8;
            border-top: 1px solid #ccc;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }

        .contact-section {
            max-width: 800px;
        }
    </style>

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-60WBWC80X3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-60WBWC80X3');
    </script>

</head>
<body>
    <!-- Left Ad Placeholder -->
    <div id="left-ad">
        <!-- Replace with your AdSense (or other) code -->
        <h4>Left Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Right Ad Placeholder -->
    <div id="right-ad">
        <!-- Replace with your AdSense code -->
        <h4>Right Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <div id="main-content">
        <!-- Simple nav links (Home, About) -->
        <div class="top-nav">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="privacy.html">Privacy</a>
            <a href="terms.html">Terms</a>
            <a href="disclaimer.html">Disclaimer</a>
            <a href="cookie.html">Cookie Policy</a>
            <a href="donate.html">Donate</a>
        </div>

        <h1>Disclaimer</h1>
        <div class="disclaimer-section">
            <p>
                The information provided on tradingtrendz.in by me is for general informational
                and educational purposes only. I am not SEBI Registered and I do not offer any financial advice.
                I are not liable for any of your losses arising from the use of data on this website. I do not
                sell any "Premium" or "Paid" features on my website. All features, tools, charts on this 
                website is available for free without signup/registration. I do not operate any Telegram/WhatsApp groups
                or similar platforms. I do not sell courses or services or initiate/engage in calls, emails, or messages 
                for monetary gain or course sales. Beware of such fraudulent schemes. I am not liable if you fall 
                victim to such scams without reading this notice. My official social media profiles, if any, will be
                listed on this website. If a social media profile is not listed here, it is not mine and should be 
                considered fake—so please beware.
            </p>
            <p>
                Any reference to past or potential performance of assets is not a guarantee 
                or indication of future outcomes. You are solely responsible for your own 
                investment decisions.
            </p>
            <p>
                I make no representations or warranties of any kind about the completeness, 
                accuracy, or reliability of the site content. Any reliance you place on such 
                information is strictly at your own risk.
            </p>
        </div>    
    </div>

    <!-- Bottom Ad Placeholder -->
    <div id="bottom-ad">
        <!-- Replace with your AdSense code -->
        <h4>Bottom Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>
</body>
</html>
"""

    # ===============================
    # 9) COOKIE PAGE HTML
    # ===============================
    cookie_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Cookie Policy</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        /* Left ad column */
        #left-ad {
            position: fixed;
            left: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-right: 1px solid #ccc;
            padding: 10px;
        }

        /* Right ad column */
        #right-ad {
            position: fixed;
            right: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-left: 1px solid #ccc;
            padding: 10px;
        }

        /* Main content area (center) */
        #main-content {
            margin: 0 180px;  /* leaves space for side ads */
            padding: 20px;
        }

        /* Navigation bar or top links */
        .top-nav {
            margin-bottom: 20px;
        }
        .top-nav a {
            margin-right: 15px;
            text-decoration: none;
            color: #0073aa;
            font-weight: bold;
        }
        .top-nav a:hover {
            text-decoration: underline;
        }

        /* Bottom ad area */
        #bottom-ad {
            background: #f8f8f8;
            border-top: 1px solid #ccc;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }

        .contact-section {
            max-width: 800px;
        }
    </style>

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-60WBWC80X3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-60WBWC80X3');
    </script>

</head>
<body>
    <!-- Left Ad Placeholder -->
    <div id="left-ad">
        <!-- Replace with your AdSense (or other) code -->
        <h4>Left Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Right Ad Placeholder -->
    <div id="right-ad">
        <!-- Replace with your AdSense code -->
        <h4>Right Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <div id="main-content">
        <!-- Simple nav links (Home, About) -->
        <div class="top-nav">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="privacy.html">Privacy</a>
            <a href="terms.html">Terms</a>
            <a href="disclaimer.html">Disclaimer</a>
            <a href="cookie.html">Cookie Policy</a>
            <a href="donate.html">Donate</a>
        </div>

        <h1>Cookie Policy</h1>
        <div class="cookie-section">
            <p>
                This Cookie Policy explains how tradingtrendz.in uses cookies and similar 
                technologies to recognize you when you visit this website.
            </p>
            <h3>What Are Cookies?</h3>
            <p>
                Cookies are small data files placed on your computer or mobile device 
                when you visit a website. 
            </p>
            <h3>Types of Cookies We Use</h3>
            <ul>
                <li><strong>Essential Cookies:</strong> These cookies are necessary for our website to function properly.</li>
                <li><strong>Analytics Cookies:</strong> We use these cookies to understand user behavior and improve our site.</li>
                <li><strong>Advertising Cookies:</strong> These cookies help deliver relevant ads and track campaign performance.</li>
            </ul>
            <h3>Managing Cookies</h3>
            <p>
                You can control or delete cookies through your browser settings. However, 
                disabling certain cookies may limit your experience on our site.
            </p>
        </div>    
    </div>

    <!-- Bottom Ad Placeholder -->
    <div id="bottom-ad">
        <!-- Replace with your AdSense code -->
        <h4>Bottom Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>
</body>
</html>
"""

    # ===============================
    # 9) DONATE PAGE HTML
    # ===============================
    donate_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Donate - tradingtrendz.in</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        /* Left ad column */
        #left-ad {
            position: fixed;
            left: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-right: 1px solid #ccc;
            padding: 10px;
        }

        /* Right ad column */
        #right-ad {
            position: fixed;
            right: 0;
            top: 0;
            width: 160px;
            height: 100%;
            background: #f8f8f8;
            border-left: 1px solid #ccc;
            padding: 10px;
        }

        /* Main content area (center) */
        #main-content {
            margin: 0 180px;  /* leaves space for side ads */
            padding: 20px;
        }

        /* Navigation bar or top links */
        .top-nav {
            margin-bottom: 20px;
        }
        .top-nav a {
            margin-right: 15px;
            text-decoration: none;
            color: #0073aa;
            font-weight: bold;
        }
        .top-nav a:hover {
            text-decoration: underline;
        }

        /* Bottom ad area */
        #bottom-ad {
            background: #f8f8f8;
            border-top: 1px solid #ccc;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }

        h1 {
            margin-top: 0;
        }
        p {
            line-height: 1.6;
        }
    </style>

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-60WBWC80X3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-60WBWC80X3');
    </script>

</head>
<body>
    <!-- Left Ad Placeholder -->
    <div id="left-ad">
        <!-- Replace with your AdSense (or other) code -->
        <h4>Left Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <!-- Right Ad Placeholder -->
    <div id="right-ad">
        <!-- Replace with your AdSense code -->
        <h4>Right Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>

    <div id="main-content">
        <!-- Top navigation -->
        <div class="top-nav">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="privacy.html">Privacy</a>
            <a href="terms.html">Terms</a>
            <a href="disclaimer.html">Disclaimer</a>
            <a href="cookie.html">Cookie Policy</a>
            <a href="donate.html">Donate</a>
        </div>

        <h1>Support tradingtrendz.in</h1>
        <p>
            Maintaining a website involves costs such as domain renewal, hosting, and other
            resources. If you’ve found value in my free website,
            please consider making a donation to help keep tradingtrendz.in running.
        </p>
        <p>
            Any amount is appreciated and goes directly toward covering operational expenses
            and improving future website services.
        </p>
        <p>
            <strong>Thank you for your support!</strong>
        </p>

        <p>
            <strong>UPI: mailtothedeveloper@okicici</strong>
        </p>

        <p>
            <strong>Paypal: paypal.me/prathikm</strong>
        </p>

    </div>

    <!-- Bottom Ad Placeholder -->
    <div id="bottom-ad">
        <!-- Replace with your AdSense code -->
        <h4>Bottom Ad Space</h4>
        <p>Promote Your Brand – Contact for Ad Placement!</p>
    </div>
</body>
</html>
"""

    # ===============================
    # L) Write all HTML files
    # ===============================

    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(home_html)
    print("Generated 'index.html' successfully!")

    with open(os.path.join(BASE_DIR, "about.html"), "w", encoding="utf-8") as f:
        f.write(about_html)
    print("Generated 'about.html' successfully!")

    with open(os.path.join(BASE_DIR, "contact.html"), "w", encoding="utf-8") as f:
        f.write(contact_html)
    print("Generated 'contact.html' successfully!")

    with open(os.path.join(BASE_DIR, "privacy.html"), "w", encoding="utf-8") as f:
        f.write(privacy_html)
    print("Generated 'privacy.html' successfully!")

    with open(os.path.join(BASE_DIR, "terms.html"), "w", encoding="utf-8") as f:
        f.write(terms_html)
    print("Generated 'terms.html' successfully!")

    with open(os.path.join(BASE_DIR, "disclaimer.html"), "w", encoding="utf-8") as f:
        f.write(disclaimer_html)
    print("Generated 'disclaimer.html' successfully!")

    with open(os.path.join(BASE_DIR, "cookie.html"), "w", encoding="utf-8") as f:
        f.write(cookie_html)
    print("Generated 'cookie.html' successfully!")

    with open(os.path.join(BASE_DIR, "donate.html"), "w", encoding="utf-8") as f:
        f.write(donate_html)
    print("Generated 'donate.html' successfully!")


    """ with open("index.html", "w", encoding="utf-8") as f:
        f.write(home_html)
    print("Generated 'index.html' successfully!")

    with open("about.html", "w", encoding="utf-8") as f:
        f.write(about_html)
    print("Generated 'about.html' successfully!")

    with open("contact.html", "w", encoding="utf-8") as f:
        f.write(contact_html)
    print("Generated 'contact.html' successfully!")

    with open("privacy.html", "w", encoding="utf-8") as f:
        f.write(privacy_html)
    print("Generated 'privacy.html' successfully!")

    with open("terms.html", "w", encoding="utf-8") as f:
        f.write(terms_html)
    print("Generated 'terms.html' successfully!")

    with open("disclaimer.html", "w", encoding="utf-8") as f:
        f.write(disclaimer_html)
    print("Generated 'disclaimer.html' successfully!")

    with open("cookie.html", "w", encoding="utf-8") as f:
        f.write(cookie_html)
    print("Generated 'cookie.html' successfully!")

    with open("donate.html", "w", encoding="utf-8") as f:
        f.write(donate_html)
    print("Generated 'donate.html' successfully!") """

if __name__ == "__main__":
    main()
