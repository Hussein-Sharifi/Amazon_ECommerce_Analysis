# Import Dependencies
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pandas_cleaning import project_root
sns.set_theme()


# Load Data
data_path = os.path.join(project_root, 'data', 'processed')
dataframes = {}
def clean_csvname(filename):
    return filename.replace('.csv', '')
for file in os.listdir(data_path):
    if file.endswith('.csv'):
        name = clean_csvname(file)
        dataframes[name] = pd.read_csv(os.path.join(data_path, file))


# Relabel dupatta category
dataframes['sales']['category'] = dataframes['sales']['category'].replace({'dupatta': 'ethnic dress'})

# Plot number of items by category
dataframes['sales']['category'].value_counts().plot(kind='barh')
plt.xlabel('Number of items')
plt.ylabel('')
plt.title('Number of Items By Category')
plt.savefig(project_root + '/outputs/figures/item_count_by_category.png', dpi=300, facecolor='white', bbox_inches='tight')
plt.close()

# Split topsellers from sales
dataframes['sales']['top_seller'] = (
    (dataframes['sales']['total_orders'] > dataframes['sales']['total_orders'].quantile(0.8)) |
    (dataframes['sales']['revenue'] > dataframes['sales']['revenue'].quantile(0.8))
    )
topsellers = dataframes['sales'][dataframes['sales']['top_seller']==True]
sales = dataframes['sales'][dataframes['sales']['top_seller']==False]


# Plot item order count and revenue distributions by category
plt.subplots(1,2, figsize=(12, 5))
# First plot: item order count distribution by category
plt.subplot(1, 2, 1)
sns.violinplot(data=sales, y='total_orders', x='category', hue='category', cut=0, inner='box')
plt.title('Item Order Count Distribution by Category')
plt.xticks(rotation=45)
plt.xlabel('')
plt.ylabel('total orders')
# Second plot: item revenue distribution by category
plt.subplot(1, 2, 2)
sns.violinplot(data=sales, y='revenue', x='category', hue='category', cut=0, inner='box')
plt.title('Item Revenue Distribution by Category')
plt.xticks(rotation=45)
plt.xlabel('')
plt.savefig(project_root + '/outputs/figures/item_distributions_by_category.png', dpi=300, facecolor='white', bbox_inches='tight')
plt.close()


# Plot median and mean item order count
plt.subplot(1, 2, 1)
sns.barplot(data=sales, x='total_orders', y='category', hue='category', estimator=np.median)
plt.title('Median Item Order Count')
plt.ylabel('')
plt.tight_layout()
plt.subplot(1, 2, 2)
sns.barplot(data=sales, x='total_orders', y='category', hue='category', estimator=np.mean)
plt.title('Mean Item Order Count')
plt.ylabel('')
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/order_count_skewness.png', dpi=300, facecolor='white')

# Plot median and mean item revenue
plt.subplot(1, 2, 1)
sns.barplot(data=sales, x='revenue', y='category', hue='category', estimator=np.median)
plt.title('Median Item Revenue')
plt.ylabel('')
plt.tight_layout()
plt.subplot(1, 2, 2)
sns.barplot(data=sales, x='revenue', y='category', hue='category', estimator=np.mean)
plt.title('Mean Item Revenue')
plt.ylabel('')
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/revenue_skewness.png', dpi=300, facecolor='white')
plt.close()


# Plot order density relative to median unit price
plt.subplots(1, 2, figsize=(12, 5))
plt.subplot(1, 2, 1)
sns.kdeplot(data=sales, x='median_unit_price', hue='category', fill=True, multiple='stack', warn_singular=False)
plt.title('Density of Orders by Median Unit Price and Category', fontsize=12)
plt.xlabel('Median Unit Price', fontsize=9)
plt.ylabel('Density', fontsize=9)
# Plot percentage of orders at a discount
plt.subplot(1, 2, 2)
sales['discount_percentage'] = sales['orders_at_discount']/sales['total_orders'] * 100
sns.barplot(data=sales, x='category', y='discount_percentage', hue='category', legend=False)
plt.title('Discounted Orders Percentage by Category')
plt.xticks(rotation=30)
plt.xlabel('')
plt.ylabel('Percentage')
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/order_density_and_discount.png', dpi=300, facecolor='white')
plt.close()


# Plot median unit price distributions per category
g = sns.displot(
    data=sales,
    x='median_unit_price',
    col='category',
    hue='category',
    kde=True,
    col_wrap=3,  
    height=4,
    legend=False,
    facet_kws={'sharex': False, 'sharey': False}
)
g.fig.suptitle('Price Distribution by Category', y=1.02)
g.set_titles("{col_name}")
g.set_axis_labels("Median Unit Price", "Count")
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/price_distribution.png', dpi=300, facecolor='white')
plt.close()


# Plot item order and revenue distributions by category
plt.subplots(1,2, figsize=(12, 5))
plt.subplot(1, 2, 1)
sns.violinplot(data=topsellers, y='total_orders', x='category', hue='category', cut=0, inner='box', palette='Paired')
plt.title('Topsellers Item Order Count Distribution by Category')
plt.xticks(rotation=45)
plt.xlabel('')
plt.ylabel('total orders')
plt.subplot(1, 2, 2)
sns.violinplot(data=topsellers, y='revenue', x='category', hue='category', cut=0, inner='box', palette='Paired')
plt.title('Topsellers Item Revenue Distribution by Category')
plt.xticks(rotation=45)
plt.xlabel('')
plt.savefig(project_root + '/outputs/figures/topseller_distributions_by_category.png', dpi=300, facecolor='white', bbox_inches='tight')
plt.close()


# Plot western dress top 20 sellers
top20_WD= topsellers[topsellers['category']=='western dress'].sort_values('total_orders', ascending=False).iloc[:20].copy()
top20_WD['non_discounted'] = top20_WD['total_orders'] - top20_WD['orders_at_discount']
plt.figure(figsize=(12, 9))
discounted_bars = plt.barh(top20_WD['asin'], top20_WD['orders_at_discount'], 
                 color='#b7cf9b', label='Discounted Orders')
nondiscounted_bars = plt.barh(top20_WD['asin'], top20_WD['non_discounted'], 
                 left=top20_WD['orders_at_discount'], 
                 color='#5d669e', label='Full-Price Orders')

# Add revenue labels
for i, (total, rev) in enumerate(zip(top20_WD['total_orders'], top20_WD['revenue'])):
    label = f"{rev:,.0f}"
    plt.text(total + 5, i, label, va='center', ha='left', fontsize=9, color='black')

plt.xlabel('Total Orders', fontsize=12)
plt.title('Top 20 Western Dress Sellers (Discounted vs Full Price)')
plt.gca().invert_yaxis()
plt.legend(frameon=True)
plt.tight_layout()
max_orders = top20_WD['total_orders'].max()
plt.xlim(0, max_orders * 1.1)
plt.savefig(project_root + '/outputs/figures/top20_WDproducts.png', dpi=300, facecolor='white')
plt.close()


# Plot Kurta top 20 sellers
top20_K= topsellers[topsellers['category']=='kurta'].sort_values('total_orders', ascending=False).iloc[:20].copy()
top20_K['non_discounted'] = top20_K['total_orders'] - top20_K['orders_at_discount']
plt.figure(figsize=(12, 9))
discounted_bars = plt.barh(top20_K['asin'], top20_K['orders_at_discount'], 
                 color='#b7cf9b', label='Discounted Orders')
nondiscounted_bars = plt.barh(top20_K['asin'], top20_K['non_discounted'], 
                 left=top20_K['orders_at_discount'], 
                 color='#5d669e', label='Full-Price Orders')

# Add revenue labels
for i, (total, rev) in enumerate(zip(top20_K['total_orders'], top20_K['revenue'])):
    label = f"{rev:,.0f}"
    plt.text(total + 5, i, label, va='center', ha='left', fontsize=9, color='black')

plt.xlabel('Total Orders', fontsize=12)
plt.title('Top 20 Kurta Sellers (Discounted vs Full Price)')
plt.gca().invert_yaxis()
plt.legend(frameon=True)
plt.tight_layout()
max_orders = top20_K['total_orders'].max()
plt.xlim(0, max_orders * 1.1)
plt.savefig(project_root + '/outputs/figures/top20_Kproducts.png', dpi=300, facecolor='white')
plt.close()


# Plot set top 20 sellers
top20_S= topsellers[topsellers['category']=='set'].sort_values('total_orders', ascending=False).iloc[:20].copy()
top20_S['non_discounted'] = top20_S['total_orders'] - top20_S['orders_at_discount']
plt.figure(figsize=(12, 9))
discounted_bars = plt.barh(top20_S['asin'], top20_S['orders_at_discount'], 
                 color='#b7cf9b', label='Discounted Orders')
nondiscounted_bars = plt.barh(top20_S['asin'], top20_S['non_discounted'], 
                 left=top20_S['orders_at_discount'], 
                 color='#5d669e', label='Full-Price Orders')

# Add revenue labels
for i, (total, rev) in enumerate(zip(top20_S['total_orders'], top20_S['revenue'])):
    label = f"{rev:,.0f}"
    plt.text(total + 5, i, label, va='center', ha='left', fontsize=9, color='black')

plt.xlabel('Total Orders', fontsize=12)
plt.title('Top 20 Sets Sellers (Discounted vs Full Price)')
plt.gca().invert_yaxis()
plt.legend(frameon=True)
plt.tight_layout()
max_orders = top20_S['total_orders'].max()
plt.xlim(0, max_orders * 1.1)
plt.savefig(project_root + '/outputs/figures/top20_Set_products.png', dpi=300, facecolor='white')
plt.close()


# Plot topseller order density relative to median unit price
plt.subplots(1, 2, figsize=(12, 5))
plt.subplot(1, 2, 1)
sns.kdeplot(data=topsellers, x='median_unit_price', hue='category', fill=True, multiple='stack')
plt.title('Topseller Density of Orders by Median Unit Price and Category', fontsize=12)
plt.xlabel('Median Unit Price', fontsize=9)
plt.ylabel('Density', fontsize=9)

# Plot percentage of orders at a discount
plt.subplot(1, 2, 2)
topsellers['discount_percentage'] = topsellers['orders_at_discount']/topsellers['total_orders'] * 100
sns.barplot(data=sales, x='category', y='discount_percentage', hue='category', legend=False)
plt.title('Topseller Discounted Orders Percentage by Category')
plt.xticks(rotation=30)
plt.xlabel('')
plt.ylabel('Percentage')
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/topseller_order_density_and_discount.png', dpi=300, facecolor='white')
plt.close()


# Plot topseller median unit price distributions
g = sns.displot(
    data=topsellers,
    x='median_unit_price',
    col='category',
    hue='category',
    kde=True,
    col_wrap=3,  
    height=6,
    legend=False,
    facet_kws={'sharex': False, 'sharey': False}
)
g.fig.suptitle('Topsellers Price Distribution by Category', y=1.02)
g.set_titles("{col_name}")
g.set_axis_labels("Median Unit Price", "Count")
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/topseller_price_distribution.png', dpi=300, facecolor='white')
plt.close()


# Plot aggregates of topsellers and regular sellers
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
# Plot topsellers aggregates
aggregates = topsellers.groupby('category').agg({'total_orders': 'sum', 'revenue': 'sum'}).reset_index().sort_values(by='revenue', ascending=False)
sns.barplot(data=aggregates, x='total_orders', y='category', hue='category', ax=ax1)
ax1.set_xlabel('Total Orders', fontsize=12)
ax1.set_ylabel('')
ax1.set_title('Topseller Total Orders', fontsize=14)
sns.barplot(data=aggregates, x='revenue', y='category', hue='category', ax=ax3)
ax3.set_xlabel('Revenue', fontsize=12)
ax3.set_ylabel('')
ax3.set_title('Topseller Total Revenue', fontsize=14)

# Plot regular sellers aggregates
aggregates_r = sales.groupby('category').agg({'total_orders': 'sum', 'revenue': 'sum'}).reset_index().sort_values(by='revenue', ascending=False)
sns.barplot(data=aggregates_r, x='total_orders', y='category', hue='category', ax=ax2)
ax2.set_xlabel('Total Orders', fontsize=12)
ax2.set_ylabel('')
ax2.set_title('Regular Sellers Total Orders', fontsize=14)
ax2.sharey(ax1)
ax2.set_xlim(ax1.get_xlim())
sns.barplot(data=aggregates_r, x='revenue', y='category', hue='category', ax=ax4)
ax4.set_xlabel('Revenue', fontsize=12)
ax4.set_ylabel('')
ax4.set_title('Regular Sellers Total Revenue', fontsize=14)
ax4.sharey(ax3)
ax4.set_xlim(ax3.get_xlim())
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/sales_aggregates.png', dpi=300, facecolor='white')
plt.close()


# Define cancellation dataframe
cancellations = dataframes['orders'].copy()
cancellations.replace({'category': 'dupatta'}, {'category': 'ethnic dress'}, inplace=True)
cancellations['is_cancelled'] = cancellations['status'] == 'cancelled or returned'

# Compute cancellation percentages for categorical columns
categorical_cols = ['category', 'size', 'sales_channel', 'ship_service_level', 
                    'fulfillment', 'style', 'b2b', 'ship_state_or_territory']

cancel_percentage = {}
for col in categorical_cols:
    cat_cancelled = cancellations.groupby(col)['is_cancelled'].sum()
    cat_totals = cancellations.groupby(col)['index_id'].count()
    cancel_percentage[col] = (cat_cancelled/cat_totals).sort_values(ascending=False) * 100


# Plot cancellation percentages for categorical columns with few unique values
for cat in ['sales_channel', 'fulfillment', 'ship_service_level', 'category', 'size', 'b2b']:
    ax = sns.barplot(
        x=cancel_percentage[cat].values, 
        y=cancel_percentage[cat].index, 
        hue=cancel_percentage[cat].index, 
        palette='flare'
    )
    # Add percentage labels to the bars
    for i, v in enumerate(cancel_percentage[cat].values):
        ax.text(
            v + 1,
            i,
            f'{v:.1f}%',
            va='center',
        )
    plt.title(f"Relative Percentage of Cancellations by {cat.replace('_', ' ').title()}")
    plt.xlim(0, 105)
    plt.savefig(
        os.path.join(project_root, 'outputs', 'figures', f'cancellation_percentage_by_{cat}.png'), 
        dpi=300, 
        facecolor='white',
        bbox_inches='tight'
    )
    plt.close()


# Plot order total amount distributions by status
sns.kdeplot(dataframes['orders'], x='amount', hue='status', fill=True, multiple='stack')
plt.xlabel('Order Total Amount')
plt.title('Order Total Amount Distribution by Status')
plt.savefig(project_root + '/outputs/figures/order_total_amount_distribution.png', dpi=300, facecolor='white', bbox_inches='tight')
plt.close()


# Export correlation matrix for cancellations as CSV
cancellation_corr = cancellations[['amount', 'quantity', 'is_cancelled']].corr()
cancellation_corr.to_csv(os.path.join(project_root, 'outputs', 'tables', 'cancellation_correlation.csv'))


# Plot cancellation percentages by ship state or territory
pivot = cancellations.pivot_table(
    values=['is_cancelled', 'index_id'],
    index='ship_state_or_territory',
    aggfunc=
    {'is_cancelled' : 'mean',
    'index_id' : 'count'},
)
pivot['is_cancelled'] = pivot['is_cancelled'] * 100
pivot.columns = ['total order count', 'cancellation percentage']

plt.figure(figsize=(12, 10))
sns.heatmap(pivot, cmap='rocket_r', vmin=100, vmax=20000, annot=True, fmt=".1f")
plt.title('Cancellation Percentages by State or Territory')
plt.ylabel('State or Territory')
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/cancellation_percentage_by_state.png', dpi=300, facecolor='white')
plt.close()


# Time analysis of shipment status
dataframes['orders']['date'] = pd.to_datetime(dataframes['orders']['date'])
plt.figure(figsize=(12, 5))
sns.kdeplot(data=dataframes['orders'], x='date', hue='status', fill=True, multiple='stack', palette='rocket')
plt.title('Shipment Status Over Time')
plt.savefig(project_root + '/outputs/figures/shipment_status_time_analysis.png', dpi=300, facecolor='white')
plt.close()


# Export top 10 states/territories sales data as CSV
top_regions = dataframes['regional_sales'].head(10)['ship_state_or_territory'].tolist()
dataframes['regional_demand'] = dataframes['regional_demand'].replace({'category': 'dupatta'}, {'category': 'ethnic dress'})
top_regions_item_sales = dataframes['regional_demand'][dataframes['regional_demand']['ship_state_or_territory'].isin(top_regions)]
top_regions_item_sales.to_csv(os.path.join(project_root, 'data', 'processed', 'top_regions_item_sales.csv'), index=False)


# Sum orders by region and category and export as CSV
regional_top_categories = top_regions_item_sales.groupby(['ship_state_or_territory', 'category']).agg({'regional_orders': 'sum'}).reset_index()
regional_top_categories.sort_values(by=['ship_state_or_territory', 'regional_orders'], ascending=False, inplace=True)
regional_top_categories.reset_index(drop=True, inplace=True)
regional_top_categories.to_csv(os.path.join(project_root, 'outputs', 'tables', 'regional_top_categories.csv'), index=False)

# Plot regional orders by category
# Pivot data to region vs category and plot
pivot = regional_top_categories.pivot_table(
    index='ship_state_or_territory',
    columns='category',
    values='regional_orders'
)
pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
pivot.plot(kind='barh', stacked=True, figsize=(7, 5))
plt.title("Regional Orders by Category")
plt.xlabel("Total Orders")
plt.ylabel("State or Territory")
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/regional_orders_by_category.png', dpi=300, facecolor='white')
plt.close()


# Plot regional order percentages by category
category_order_percentages = pivot
total_orders = pivot.sum(axis=1)
for col in pivot:
    category_order_percentages[col] = category_order_percentages[col]/total_orders * 100

category_order_percentages.plot(kind='barh', stacked=True, figsize=(7,5))
plt.title("Order Percentage by Category")
plt.xlabel("Percent")
plt.ylabel("State or Territory")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/regional_order_percentages_by_category.png', dpi=300, facecolor='white')
plt.close()


# Plot cancellation rates heat map by region and category
top_categories = ['set', 'kurta', 'top', 'western dress']

grouped = cancellations[
    (cancellations['ship_state_or_territory'].isin(top_regions)) & 
    (cancellations['category'].isin(top_categories))
].groupby(['ship_state_or_territory', 'category']).agg(
    total_orders=('index_id', 'count'),
    cancellations=('is_cancelled', 'sum')
).reset_index()
grouped['cancel_rate'] = grouped['cancellations'] / grouped['total_orders']

pivot = grouped.pivot_table(
    index='ship_state_or_territory',
    columns= 'category',
    values='cancel_rate'
)

plt.figure(figsize=(7, 7))
sns.heatmap(pivot * 100, cmap='Reds', annot=False, fmt=".1f", linewidths=0.5)
plt.title("Cancellation Rate (%) by Category and Region")
plt.ylabel("Category")
plt.xlabel("Region")
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/cancellation_rate_heatmap.png', dpi=300, facecolor='white')
plt.close()


# Compute category average cancellation rates.
global_avg = grouped.groupby('category')['cancel_rate'].mean()
# Calculate deviation and plot
grouped['cancel_diff'] = grouped.apply(
    lambda x: x['cancel_rate'] - global_avg[x['category']], axis=1
)
plt.figure(figsize=(12, 6))
sns.barplot(
    data=grouped,
    x='category',
    y='cancel_diff',
    hue='ship_state_or_territory',
    palette='deep'
)
plt.axhline(0, color='black', linewidth=0.8)
plt.title("Cancellation Rate Deviation from Average by Category and Region")
plt.ylabel("Deviation")
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(project_root + '/outputs/figures/cancellation_rate_deviation.png', dpi=300, facecolor='white')
plt.close()