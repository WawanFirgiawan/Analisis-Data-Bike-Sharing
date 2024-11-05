import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# Memuat data dari file CSV
df_day = pd.read_csv("day.csv")

# Menghapus kolom yang tidak diperlukan
df_day.drop(columns=['windspeed'], inplace=True)

# Mengubah nama kolom
df_day.rename(columns={
    'dteday': 'dateday',
    'yr': 'year',
    'mnth': 'month',
    'cnt': 'count'
}, inplace=True)

# Mengonversi angka menjadi deskripsi
month_mapping = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
weekday_mapping = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}

df_day['month'] = df_day['month'].map(month_mapping)
df_day['season'] = df_day['season'].map(season_mapping)
df_day['weekday'] = df_day['weekday'].map(weekday_mapping)

# Membuat komponen filter
min_date = pd.to_datetime(df_day['dateday']).dt.date.min()
max_date = pd.to_datetime(df_day['dateday']).dt.date.max()

with st.sidebar:
    st.image(
        'sota.png')

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = df_day[(df_day['dateday'] >= str(start_date)) &
                 (df_day['dateday'] <= str(end_date))]

# Fungsi untuk membuat dataframe agregat
def create_aggregated_df(df, groupby_col, agg_col):
    return df.groupby(by=groupby_col).agg({agg_col: 'sum'}).reset_index()

# Menyiapkan dataframe agregat
daily_rent_df = create_aggregated_df(df_day, 'dateday', 'count')
daily_casual_rent_df = create_aggregated_df(df_day, 'dateday', 'casual')
daily_registered_rent_df = create_aggregated_df(df_day, 'dateday', 'registered')
season_rent_df = df_day.groupby(by='season')[['registered', 'casual']].sum().reset_index()
monthly_rent_df = create_aggregated_df(df_day, 'month', 'count').reindex(month_mapping.values(), fill_value=0)
weekday_rent_df = create_aggregated_df(df_day, 'weekday', 'count')
workingday_rent_df = create_aggregated_df(df_day, 'workingday', 'count')
holiday_rent_df = create_aggregated_df(df_day, 'holiday', 'count')
weather_rent_df = create_aggregated_df(df_day, 'weathersit', 'count')

# Membuat komponen filter
min_date = df_day['dateday'].min()
max_date = df_day['dateday'].max()

# Membuat Dashboard
st.header('Bike Rental By Wawan Firgiawan')

# Penyewaan harian
st.subheader('Daily Rentals')
col1, col2, col3 = st.columns(3)

with col1:
    st.metric('Casual', value=daily_casual_rent_df['casual'].sum())
with col2:
    st.metric('Registered', value=daily_registered_rent_df['registered'].sum())
with col3:
    st.metric('Total User', value=daily_rent_df['count'].sum())

# Penyewaan berdasarkan musim
st.subheader('Seasonly Rentals')
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x='season', y='registered', data=season_rent_df, color='tab:blue', ax=ax)
sns.barplot(x='season', y='casual', data=season_rent_df, color='tab:orange', ax=ax)

for index, row in season_rent_df.iterrows():
    ax.text(index, row['registered'], str(row['registered']), ha='center', va='bottom', fontsize=12)
    ax.text(index, row['casual'], str(row['casual']), ha='center', va='bottom', fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=15)
ax.legend()
st.pyplot(fig)

# Penyewaan berdasarkan kondisi cuaca
st.subheader('Weatherly Rentals')
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x=weather_rent_df.index, y=weather_rent_df['count'], palette=["tab:blue", "tab:orange", "tab:green"], ax=ax)

for index, row in enumerate(weather_rent_df['count']):
    ax.text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)

# Penyewaan berdasarkan weekday, working, dan holiday
st.subheader('Weekday, Workingday, and Holiday Rentals')
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10))

# Berdasarkan workingday
sns.barplot(x='workingday', y='count', data=workingday_rent_df, palette=["tab:blue", "tab:orange"], ax=axes[0])
for index, row in enumerate(workingday_rent_df['count']):
    axes[0].text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)
axes[0].set_title('Number of Rents based on Working Day')
axes[0].tick_params(axis='x', labelsize=15)
axes[0].tick_params(axis='y', labelsize=10)

# Berdasarkan holiday
sns.barplot(x='holiday', y='count', data=holiday_rent_df, palette=["tab:blue", "tab:orange"], ax=axes[1])
for index, row in enumerate(holiday_rent_df['count']):
    axes[1].text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)
axes[1].set_title('Number of Rents based on Holiday')
axes[1].tick_params(axis='x', labelsize=15)
axes[1].tick_params(axis='y', labelsize=10)

# Berdasarkan weekday
sns.barplot(x='weekday', y='count', data=weekday_rent_df, palette=["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink"], ax=axes[2])
for index, row in enumerate(weekday_rent_df['count']):
    axes[2].text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)
axes[2].set_title('Number of Rents based on Weekday')
axes[2].tick_params(axis='x', labelsize=15)
axes[2].tick_params(axis='y', labelsize=10)

plt.tight_layout()
st.pyplot(fig)

# Menampilkan hak cipta
st.caption('Copyright (c) Wawan Firgiawan 2024')
