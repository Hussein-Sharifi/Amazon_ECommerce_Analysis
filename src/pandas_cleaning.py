# Import dependencies
import numpy as np
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt


# Read data file and inspect dataset
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(project_root, 'data', 'raw', 'amazon_sales_report.csv')
amazon_sales = pd.read_csv(file_path)


# Normalize column names
amazon_sales.columns = (amazon_sales.columns.str.strip()
                        .str.replace(r'[-\s]', '_', regex=True)
                        .str.lower())
amazon_sales.rename(columns={'qty': 'quantity', 'fulfilment': 'fulfillment'}, inplace=True)


# Drop unnamed column and convert date types
amazon_sales.drop(columns='unnamed:_22', inplace=True)
amazon_sales['date'] = pd.to_datetime(
    amazon_sales['date'], 
    format='%m-%d-%y'
)
categorical_columns = [
    'status', 'fulfillment', 'sales_channel', 'ship_service_level', 
    'category', 'size', 'courier_status', 'currency', 'ship_state',
    'ship_country', 'fulfilled_by'
]
string_columns = [
    'order_id', 'style', 'sku', 'asin', 'ship_city', 'promotion_ids',
    'ship_postal_code'
]
amazon_sales[categorical_columns] = amazon_sales[categorical_columns].astype('category')
amazon_sales[string_columns] = amazon_sales[string_columns].astype('string')


# Normalize values for categorical and string columns.
uppercase_strings = ['asin', 'style', 'size', 'sku', 'currency', 'ship_country']
lowercase_strings = [col for col in (categorical_columns + string_columns) 
                                 if col not in uppercase_strings]
amazon_sales[uppercase_strings] = (
    amazon_sales[uppercase_strings]
    .apply(lambda x: x.str.strip().str.upper())
)
amazon_sales[lowercase_strings] = (
    amazon_sales[lowercase_strings]
    .apply(lambda x: x.str.strip().str.lower())
)


# Drop duplicates
amazon_sales = amazon_sales.drop_duplicates(subset=['order_id', 'asin', 'date'], keep='last')


# Fill missing shipping country values. Reconcile fulfillment columns and drop one of them.
amazon_sales['ship_country'] = amazon_sales['ship_country'].fillna("IN")
amazon_sales['fulfillment'] = amazon_sales['fulfillment'].replace({'merchant': 'easy ship'})
amazon_sales.drop(columns='fulfilled_by', inplace=True)


# Relabel categories for better consistency
amazon_sales.loc[
    (amazon_sales['category']=='dupatta') |
    (amazon_sales['category']=='saree')
    , 'category'] ='ethnic dress'


# Simplify status values and reconcile with courier status
amazon_sales.loc[
    (amazon_sales['courier_status'] == 'unshipped') |
    (amazon_sales['courier_status'] == 'cancelled'),
'status'] = 'cancelled'

amazon_sales.loc[
    (amazon_sales['courier_status'] == 'shipped') &
    (amazon_sales['status'] == 'pending'),
'status'] = 'shipped'


# Combine status as cancelled or returned. Drop statuses with 0 value count
combine_status = {
    "shipped - returned to seller": "cancelled",
    "shipped - returning to seller": "cancelled",
    "shipped - rejected by buyer": "cancelled",
    "shipped - lost in transit": "cancelled",
    "shipped - damaged": "cancelled"
}
amazon_sales['status'] = amazon_sales['status'].replace(combine_status)
amazon_sales['status'] = amazon_sales['status'].replace({'cancelled': 'cancelled or returned'})

# Drop 0 count status 
status_to_drop = ['pending', 'pending - waiting for pick up', 'shipping']
amazon_sales = amazon_sales[~amazon_sales['status'].isin(status_to_drop)]


# Drop courier_status
amazon_sales.drop(columns='courier_status', inplace=True)


# Identify incorrectly labeled states/territories
states_territories = '''Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, 
Himachal Pradesh, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, 
Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, 
Uttarakhand, West Bengal, Andaman and Nicobar Islands, Chandigarh, Dadra and Nagar Haveli and Daman and Diu, 
Delhi, Jammu and Kashmir, Ladakh, Lakshadweep, Puducherry'''
states_territories = sorted(states_territories.replace('\n', '').lower().split(', '))
amazon_sales = amazon_sales.rename(columns={'ship_state': 'ship_state_or_territory'})
incorrect_states_labels = (amazon_sales[
    ~amazon_sales['ship_state_or_territory']
    .isin(states_territories)]['ship_state_or_territory']
.unique())


# Update values
update = {
    "jammu & kashmir": "jammu and kashmir",
    "dadra and nagar": "dadra and nagar haveli and daman and diu",
    "andaman & nicobar": "andaman and nicobar islands",
    "rajshthan": "rajasthan",
    "nl": "nagaland",
    "new delhi": "delhi",
    "punjab/mohali/zirakpur": "punjab",
    "rj": "rajasthan",
    "orissa": "odisha",
    "pb": "punjab",
    "apo": "unknown",
    "ar": "arunachal pradesh",
    "pondicherry": "puducherry",
    "rajsthan": "rajasthan"
}
amazon_sales['ship_state_or_territory'] = amazon_sales['ship_state_or_territory'].replace(update)
# Fill na values and the one address with "apo" as unknown.
amazon_sales[['ship_state_or_territory', 'ship_city', 'ship_postal_code']] = (
    amazon_sales[['ship_state_or_territory', 'ship_city', 'ship_postal_code']]
    .fillna('unknown')
)


# Fix postal code decimal place and convert promotion_ids to boolean
amazon_sales['ship_postal_code'] = amazon_sales['ship_postal_code'].str.replace('\.0$', '', regex=True)
amazon_sales['promotion_ids'] = amazon_sales['promotion_ids'].notna()


# Export processed data to csv
output_path = os.path.join(project_root, 'data', 'processed', f'amazon_sales_pdcleaned.csv')
amazon_sales.to_csv(output_path, index=False)