import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe
def create_monthly_rent_df(df):
    monthly_rented_df = df.resample(rule='M', on='dteday').agg({
    "total": "sum",
    "casual": "sum",
    "registered": "sum"
})
    monthly_rented_df.index = monthly_rented_df.index.strftime('%B') #mengubah format order date menjadi Tahun-Bulan
    monthly_rented_df = monthly_rented_df.reset_index()
    
    return monthly_rented_df

def create_feature_rented_df(df, feature):
    df = df.groupby(by=feature).agg({
        "casual": "sum",
        "registered": "sum",
        "total": "sum"
    }).sort_values(by="total", ascending=False).reset_index()
    
    casual_df = df[[feature,'casual']].copy()
    casual_df['type'] = 'casual'
    casual_df = casual_df.rename(columns={'casual': 'total'})

    registered_df = df[[feature,'registered']].copy()
    registered_df['type'] = 'registered'
    registered_df = registered_df.rename(columns={'registered': 'total'})

    total_df = df[[feature,'total']].copy()
    total_df['type'] = 'total'

    new_hours_df = pd.concat([casual_df, registered_df, total_df])
    return new_hours_df


# Load cleaned data
all_df = pd.read_csv("all_data.csv")

all_df['dteday'] = pd.to_datetime(all_df['dteday'])

# Filter data
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=200)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

# st.dataframe(main_df)

# # Menyiapkan berbagai dataframe
monthly_rented_df = create_monthly_rent_df(main_df)
workingday_hourly_rented_df = create_feature_rented_df(main_df[main_df.workingday==1],'hour')
holiday_hourly_rented_df = create_feature_rented_df(main_df[main_df.workingday==0], 'hour')
season_rented_df = create_feature_rented_df(main_df, 'season_group')

# plot number of monthly rent
st.header('Dashboard BikeSharing :sparkles:')
st.subheader('Monthly renth')

col1, col2, col3 = st.columns(3)

with col1:
    total_casual = monthly_rented_df.casual.sum()
    st.metric("Total Casual", value=f"{total_casual:,d}" )

with col2:
    total_registered = monthly_rented_df.registered.sum() 
    st.metric("Total Registered", value=f"{total_registered:,d}")

with col3:
    total_total = monthly_rented_df.total.sum() 
    st.metric("Total", value=f"{total_total:,d}")


fig, ax = plt.subplots(figsize=(35, 15))

sns.lineplot(x='dteday', y='value', hue='variable', data=pd.melt(monthly_rented_df, ['dteday']), ax=ax)

ax.set_title("Number of rented bike each Month", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.legend(fontsize=40, loc=2)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)


# workingday/weekend performance
st.subheader("Workingday & Weekend/Holiday performances each hour")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

sns.barplot(data=workingday_hourly_rented_df, x="hour", y="total", hue="type", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Hour", fontsize=30)
ax[0].legend(fontsize=30, loc=2)
ax[0].set_title("Workingday performance each hour", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(data=holiday_hourly_rented_df, x="hour", y="total", hue="type", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("hour", fontsize=30)
ax[1].legend(fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Weekend/holiday performance each hour", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)


# customer demographic
st.subheader("Season performance")

fig, ax = plt.subplots(figsize=(35, 15))

sns.barplot(data=season_rented_df, x="season_group", y="total", hue="type", ax=ax)
ax.legend(fontsize=40)
ax.set_title("Season performance", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel("season")
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)


st.caption('Copyright © Muhammad Hadi 2023')