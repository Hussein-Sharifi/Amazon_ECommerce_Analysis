# Importing dependencies
import numpy as np
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Read data file and inspect dataset
file_path = os.path.join('data', 'Amazon Sale Report.csv')
amazon_sales = pd.read_csv(file_path)
print(amazon_sales.columns, "\n")
print(amazon_sales.head())

# Normalize column names and inspect info
amazon_sales.columns = (amazon_sales.columns.str.strip()
                        .str.replace(r'[-\s]', '_', regex=True)
                        .str.lower())
amazon_sales.rename(columns={'qty': 'quantity', 'fulfilment': 'fulfillment'}, inplace=True)
amazon_sales.info()

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

amazon_sales.info()

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

print(amazon_sales[uppercase_strings].head())

print(amazon_sales[lowercase_strings].head())

# Check for duplicates and missing values
print(f"Number of duplicate rows: {amazon_sales.duplicated().sum()} \n")
print(f"Number of duplicate indicies: {amazon_sales.shape[0] - amazon_sales['index'].nunique()} \n")
print(f"Number of duplicate orders ids: {amazon_sales['order_id'].duplicated().sum()} \n")
print(f"Number of null entries by column:\n{amazon_sales.isna().sum()}")

# Inspect duplicate order ids. Looks like they are multiple parts of same order. Double check this in sql
# Will decide what to do with null values during EDA
amazon_sales[amazon_sales['order_id'].duplicated(keep=False)].sort_values('order_id')


# Categorical data EDA

# Inspect unique and null values per col
cat_stats = pd.DataFrame({
    'Unique Values': [amazon_sales[col].nunique() for col in categorical_columns],
    'Null Values': [amazon_sales[col].isna().sum() for col in categorical_columns],
}, index=categorical_columns)

print(cat_stats)

# Currency null values most likely can be filled with INR, but I'll double check against amount and item price info in sql.
# Having both status and courier status might be redundant. 
# Fulfilled by is ...?

# Let's Inspect distributions
for col in categorical_columns:
    print(amazon_sales[col].value_counts(), end="\n\n")

'''128942/128975 have india as shipping country. We can fill in for the missing 33. 
fulfilled_by and fulfillment both mark orders handled by easy ship. There are 39277 of them.'''

amazon_sales['ship_country'] = amazon_sales['ship_country'].fillna("IN")
amazon_sales['fulfillment'] = amazon_sales['fulfillment'].replace({'merchant': 'easy ship'})
amazon_sales.drop(columns='fulfilled_by', inplace=True)

print(amazon_sales['fulfillment'].value_counts())
print(amazon_sales['ship_country'].isna().sum())

# We're left with status/courier_status and ship state. Other columns look good.
# Let's start with status. Inspect status vs courier status.
print(amazon_sales.groupby('status')['courier_status'].value_counts())


'''Since transportation follows order processing, courier status is more up to date than status. Also looks like orders with cancelled
status have 50/50 unshipped/cancelled courier status, meaning the terms were used interchangebly. So we make the simplifying assumption
unshipped --> cancelled '''

# Reconcile info from courier status with status.
amazon_sales.loc[
    (amazon_sales['courier_status'] == 'unshipped') |
    (amazon_sales['courier_status'] == 'cancelled'),
'status'] = 'cancelled'

amazon_sales.loc[
    (amazon_sales['courier_status'] == 'shipped') &
    (amazon_sales['status'] == 'pending'),
'status'] = 'shipped'

print(amazon_sales.groupby('status')['courier_status'].value_counts())
print(f"\n{amazon_sales['status'].value_counts()}")

'''Considering ambiguity in cancelled shipment status, we won't be able to meaningfully distinguish between orders cancelled before
shipment and orders we had to ship back for cost analysis. Instead, let's focus on analyzing consumer choices vis a vie cancellation.
For this reason, I'll combine different categories as cancelled'''

# Combine cancelled status. Drop status with 0 value count
combine_status = {
    "shipped - returned to seller": "cancelled",
    "shipped - returning to seller": "cancelled",
    "shipped - rejected by Buyer": "cancelled"
}
amazon_sales['status'] = amazon_sales['status'].replace(combine_status)
amazon_sales['status'] = amazon_sales['status'].replace({'cancelled': 'cancelled or returned'})

# All of these orders had updates in courier_status and were not updated in status. We are left with 0 order count for each. 
status_to_drop = ['pending', 'pending - waiting for pick up', 'shipping']
amazon_sales = amazon_sales[~amazon_sales['status'].isin(status_to_drop)]

print(amazon_sales['status'].value_counts())
print(amazon_sales.shape[0])

# Next, ship state. Many of the values are territories, so let's account for both
states_territories = '''Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, 
Himachal Pradesh, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, 
Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, 
Uttarakhand, West Bengal, Andaman and Nicobar Islands, Chandigarh, Dadra and Nagar Haveli and Daman and Diu, 
Delhi, Jammu and Kashmir, Ladakh, Lakshadweep, Puducherry'''
states_territories = sorted(states_territories.replace('\n', '').lower().split(', '))
print(states_territories)
print(len(states_territories))
amazon_sales = amazon_sales.rename(columns={'ship_state': 'ship_state_or_territory'})


incorrect_states_labels = (amazon_sales[
    ~amazon_sales['ship_state_or_territory']
    .isin(states_territories)]['ship_state_or_territory']
.unique())
print(f"\n Incorrectly labeled states/territories:\n {incorrect_states_labels}")

# Update values using a predictive model
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

print(amazon_sales['ship_state_or_territory'].isna().sum())
print(amazon_sales['ship_state_or_territory'].nunique())
print(sorted(amazon_sales['ship_state_or_territory'].unique()))

# String columns EDA
for col in string_columns:
    print(f"{col:<20} {amazon_sales[col].nunique()} unique values")

# Check style, sku, and asin column values. style value count < asin value count which is a good sign. 
# Let's check for unexpected characters and inspect tail end of value_counts sample for bogus values. Looks good

for col in ['style', 'asin', 'sku']:
    print(amazon_sales[amazon_sales[col].str.contains(r'[^a-zA-Z0-9\s-]', na=True)], end="\n\n")

for col in ['style', 'asin', 'sku']:
    print(amazon_sales[col].value_counts().tail(10))



