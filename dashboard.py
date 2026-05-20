import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def group_features(target_feature,type,df):
    match type:
        case 'mean':
            return(df.groupby(target_feature)['amount'].mean().reset_index())
            #return (df.groupby(target_feature, sort=False)['amount'].mean().reset_index().sort_values('amount)) sort version?
        case 'sum':
            return(df.groupby(target_feature)['amount'].sum().reset_index())

def plot_graph(target_average,target_feature,df):
    fig,ax=plt.subplots(figsize=(16,8))
    ax.bar(df[target_feature], df['amount'], color="#90CAF9")
    ax.axhline(target_average, color='red', linestyle='--', label='rata-rata')
    ax.set_title(f'Dampak {target_feature} pada amount', fontsize=20)
    ax.set_xlabel(target_feature,fontsize=20)
    ax.set_ylabel(f'amount',fontsize=20)
    ax.tick_params(axis='x',rotation=45,labelsize=20)
    ax.tick_params(axis='y',labelsize=20)
    ax.legend()
    st.pyplot(fig)

all_df=pd.read_csv("cleaned_data_v8.csv")

datetime_columns=["date"]

for column in datetime_columns:
    all_df[column]=pd.to_datetime(all_df[column])

min_date=all_df["date"].min()
max_date=all_df["date"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRPYH4zPxn-h3o-eJmfDTLtZDGM8bCiOKnspg&s")
    #SUMBER  LOGO PERUSAHAAN:https://elements.envato.com/rent-bike-logo-62Q9FHS?srsltid=AfmBOoqdOr9W4ClZC9s2kw-buABj-1vRS87bvyEd_YNgShz5vQCk73on
    start_date,end_date=st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date,max_date]
    )

main_df=all_df[(all_df["date"]>=str(start_date)) & 
                (all_df["date"]<=str(end_date))]

st.header('finedata dashboard')

target_feature=st.selectbox(
    'feature?',
    ('type','category','subcategory','payment_method','description'))
group_type=st.selectbox(
    'sum or mean?',
    ('sum','mean'))


filtered_df=group_features(target_feature,group_type,main_df)
col1,col2=st.columns(2)

total_rentals=main_df.amount.sum()
average_rentals=main_df.amount.mean().round(2)


st.subheader(total_rentals)
st.subheader(average_rentals)

plot_graph(average_rentals,target_feature,filtered_df)

st.caption('Copyright © finewise 2036')