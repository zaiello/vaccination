import requests
import json
import html
import pandas as pd
import re

# Get COVID case data
url = 'https://data.cdc.gov/resource/9mfq-cb36.json'
headers = {
    'X-App-Token': "AIccX8t5UlmYvloE9OdAxodtf",
    }
response = requests.get(url, headers=headers)
response_info = json.loads(response.text)


# Convert COVID case data into dataframe
results_df = pd.DataFrame.from_records(response_info)


# Get Covid vaccination data
url_2 = 'https://data.cdc.gov/resource/8xkx-amqh.json'
headers_2 = {
    'X-App-Token': "AIccX8t5UlmYvloE9OdAxodtf",
    }
response_vac = requests.get(url_2, headers=headers_2)
response_info_vac = json.loads(response_vac.text)


# Convert COVID case data into dataframe
results_df_vac = pd.DataFrame.from_records(response_info_vac)

# https://pandas.pydata.org/pandas-docs/version/0.8.1/indexing.html
# Filter out data that was not recorded in 2022
criterion = results_df['submission_date'].map(lambda x: x.startswith('2022'))
filtered_df = results_df[criterion]

# Parse columns of interest
# https://stackoverflow.com/questions/34682828/extracting-specific-selected-columns-to-new-dataframe-as-a-copy
parsed_df = filtered_df[['submission_date', 'state', 'conf_cases']]

# drop missing values
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html
dropped_df = parsed_df.dropna()

# Since all data from the second dataframe is from january 2022, lets make a new dataframe with our information of
# interest (percent of the population with at least one dose and state). We will merge the two dataframes on state.

# create a dataframe out of the columns of interest
new_vac_df = results_df_vac[['recip_state', 'administered_dose1_pop_pct']]

# drop missing values
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html
dropped_vac = new_vac_df.dropna()

# merge the two dataframes on 'state'
# https://stackoverflow.com/questions/33086881/merge-two-python-pandas-data-frames-of-different-length-but-keep-all-rows-in-out
final_df = dropped_df.merge(dropped_vac, how='left', left_on='state', right_on='recip_state')

# change the percent administered dose column to numeric
# https://stackoverflow.com/questions/15891038/change-column-type-in-pandas
final_df['administered_dose1_pop_pct'] = final_df['administered_dose1_pop_pct'].apply(pd.to_numeric)

# average the percent administered dose per state
# https://stackoverflow.com/questions/30482071/how-to-calculate-mean-values-grouped-on-another-column-in-pandas
ave_final_df = final_df.groupby('state', as_index=False)['administered_dose1_pop_pct'].mean()

# change the conf_cases column to numeric
final_df['conf_cases'] = final_df['conf_cases'].apply(pd.to_numeric)


# average the conf_cases by state
conf_cases_df = final_df.groupby('state', as_index=False)['conf_cases'].mean()


# merge the dataframes: ave_final_df includes the state and ave % of population with at least one dose and
# conf_cases_df includes the state and average confirmed cases per state. Merge on state.
last_df_for_real = ave_final_df.merge(conf_cases_df, on='state')


# Convert to JSON
json_list = json.loads(json.dumps(list(last_df_for_real.T.to_dict().values())))

with open('covid_data.json', 'w') as fp:
    json.dump(json_list, fp)

# Convert to CSV
last_df_for_real.to_csv('covid_data.csv')

# Convert from JSON to CSV format
json_df = pd.read_json('covid_data.json')
json_df.to_csv('converted_json.csv', index=False)

# Convert from CSV to JSON format
csv_df = pd.read_csv('covid_data.csv')
csv_df.to_json('converted_csv.json')

# Open the file
f = open('covid_data.json')

# Parse
data = json.load(f)

# print
for i in data:
    print(i)

# Close file
f.close()
