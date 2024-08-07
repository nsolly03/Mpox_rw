#add libraries
import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import os
import warnings
warnings.filterwarnings('ignore')
from collections import Counter

#Naming page
st.set_page_config(page_title="Mpoxdash", page_icon=":bar_chart:", layout="wide")

#Page title settings
st.title(" :bar_chart: Mpox Dashboard For Rwanda")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

#Uploading file
fl = st.file_uploader(":file_folder: Upload a file", type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    os.chdir(r"C:\Users\nseku\Desktop\PHS&EPR Work\Mpox\MPOX Dashboard\streamlit_dashboards")
    df = pd.read_csv("linelist.csv")

#Adding selectig date option
col1, col2 = st.columns((2))
df["Date of confirmation"] = pd.to_datetime(df["Date of confirmation"])

# Getting the min and max date
startDate = pd.to_datetime(df["Date of confirmation"]).min()
endDate = pd.to_datetime(df["Date of confirmation"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End date", endDate))

df = df[(df["Date of confirmation"] >= date1) & (df["Date of confirmation"] <= date2)].copy()

## Adding more filters

##Province selection
st.sidebar.header("Choose your filter: ")
province = st.sidebar.multiselect("Select Province", df["Province"].unique())
if not province:
    df2 = df.copy()
else:
    df2 = df[df["Province"].isin(province)]


##District selection
district = st.sidebar.multiselect("Select District", df2["District"].unique())
if not district:
    df3 = df2.copy()
else:
    df3 = df2[df2["District"].isin(district)]

#Create for sector
sector = st.sidebar.multiselect("Select the sector", df3["Sector"].unique())


##Filter the data based on Province, District and Sector
if not province and not district and not sector:
    filtered_df = df
elif not district and not sector:
    filtered_df = df[df["Province"].isin(province)]
elif not province and not sector:
    filtered_df = df[df["District"].isin(district)]
elif district and sector:
    filtered_df = df3[df["District"].isin(district) & df3["Sector"].isin(sector)]
elif province and sector:
    filtered_df = df3[df["Province"].isin(province) & df3["Sector"].isin(sector)]
elif district and district:
    filtered_df = df3[df["Province"].isin(province) & df3["District"].isin(district)]
elif sector:
    filtered_df = df3[df3["Sector"].isin(sector)]
else:
    filtered_df = df3[df3["Province"].isin(province) & df3["District"].isin(district) & df3["Sector"].isin(sector)]


##Creating an epicurve (line graph)

# Convert 'Date of confirmation' from string to datetime
filtered_df['Date of confirmation'] = pd.to_datetime(filtered_df['Date of confirmation'], format='%m/%d/%Y')

# Sort data by 'Date of confirmation'
filtered_df = filtered_df.sort_values('Date of confirmation')

# Create a new column for the week, setting the week to start on Sunday
filtered_df['week'] = filtered_df['Date of confirmation'].dt.to_period('W-SAT')

# Format the week for more readable output
filtered_df['week_str'] = filtered_df['week'].apply(lambda x: f"{x.start_time.strftime('%m/%d')} - {x.end_time.strftime('%m/%d')}")

# Group by new week column and count occurrences
weekly_cases = filtered_df.groupby('week_str').size().reset_index(name='Number of Cases')

# Creating a subheader in Streamlit
st.subheader('Weekly Epicurve of Mpox cases in Rwanda since May 2024')

# Create a histogram using Plotly
fig = px.histogram(filtered_df, x='Date of confirmation', 
                   labels={"Date of confirmation": "Date", "count": "Number of Cases"},
                   nbins=len(weekly_cases),
                   color_discrete_sequence=['darkred'])  # Set bar color to dark red

# Customize the layout
fig.update_traces(marker=dict(line=dict(color='white', width=1)))  # Add white lines between bars
fig.update_layout(bargap=0)  # Keep bars touching each other
fig.update_xaxes(title_text="Weeks")
fig.update_yaxes(title_text="Number of Mpox Cases")

# Display the figure in Streamlit
st.plotly_chart(fig)


###CREATING BAR CHART OF AGE GROUP AND SEX
# Assuming filtered_df is your existing dataframe

cl1, cl2 = st.columns((2))

with cl1:
    # First, let's create age groups
    def age_group(age):
        if age <= 15:
            return '0-15'
        elif age <= 30:
            return '16-30'
        elif age <= 45:
            return '31-45'
        elif age <= 60:
            return '46-60'
        else:
            return '60+'

    # Apply the age_group function to create a new column
    filtered_df['Age Group'] = filtered_df['Age (years)'].apply(age_group)

    # Group by age group and sex
    age_sex_groups = filtered_df.groupby(['Age Group', 'Sex']).size().reset_index(name='Count')

    # Create the stacked bar chart
    fig_stacked = px.bar(age_sex_groups, 
                         x='Age Group', 
                         y='Count', 
                         color='Sex',
                         labels={'Age Group': 'Age Group', 'Count': 'Number of Cases'},
                         category_orders={'Age Group': ['0-15', '16-30', '31-45', '46-60', '60+']})

    # Customize the layout
    fig_stacked.update_layout(barmode='stack')
    fig_stacked.update_xaxes(title_text="Age Groups")
    fig_stacked.update_yaxes(title_text="Number of Mpox Cases")

    # Display the stacked bar chart in Streamlit
    st.subheader('Distribution of Mpox Cases by Age Group and Sex')
    st.plotly_chart(fig_stacked)

with cl2:
    # Group by possible exposure and count occurrences
    exposure_counts = filtered_df.groupby('Possible exposure').size().reset_index(name='Count')

    # Calculate percentages
    total = exposure_counts['Count'].sum()
    exposure_counts['Percentage'] = 100 * exposure_counts['Count'] / total

    # Create the donut chart
    fig_donut = px.pie(exposure_counts, 
                       values='Percentage', 
                       names='Possible exposure', 
                       hole=0.5)  # The 'hole' parameter creates the donut shape

    # Customize the layout to only show percentage inside the chart
    fig_donut.update_traces(textposition='inside', textinfo='percent')

    # Display the donut chart in Streamlit
    st.subheader('Distribution of Mpox cases by possible exposures')
    st.plotly_chart(fig_donut)


# Define symptoms
symptoms = ['Rash', 'Fever', 'Headache', 'Muscle pain', 'Fatigue', 'Sorethroat', 'Nausea/vomiting', 'Cough', 'Chills/sweats']

# Transform data to 'Yes'/'No' for simplicity
df[symptoms] = df[symptoms].applymap(lambda x: 'Yes' if 'Yes' in str(x) else 'No')

# Count 'Yes' occurrences for each symptom
symptom_counts = df[symptoms].apply(lambda x: x.value_counts().get('Yes', 0))

# Sort symptoms by their frequency in descending order
sorted_symptoms = symptom_counts.sort_values(ascending=False).index

# Reorder the symptoms in the DataFrame according to their sorted order
df_sorted = df[sorted_symptoms]

# Recalculate the counts for the sorted symptoms to update the DataFrame for the heatmap
sorted_symptom_counts = df_sorted.apply(lambda x: x.value_counts().get('Yes', 0))
sorted_heatmap_data = pd.DataFrame(sorted_symptom_counts).T  # Transpose to fit heatmap requirements


# Count occurrences of each status
status_counts = df['Current status'].value_counts().reset_index()
status_counts.columns = ['Current status', 'Count']


# Create columns in Streamlit
cl1, cl2 = st.columns(2)

with cl1:
    st.subheader("Symptoms Frequency Among Mpox Cases")
    # Define the figure size for the heatmap
    plt.figure(figsize=(12, 8))  # Adjusted size for better aspect ratio
    # Create heatmap with a color bar
    ax = sns.heatmap(sorted_heatmap_data, annot=True, cmap="coolwarm", fmt="d", cbar=True)
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.yticks(rotation=0)  # Keep the y-axis labels readable
    st.pyplot(plt)

with cl2:
    st.subheader("Mpox Cases Current Situation")
    # Create a treemap with a defined figure height and custom legend title
    fig = px.treemap(
        status_counts,
        path=['Current status'],
        values='Count',
        height=400,
    )
    # Set text information for displaying counts
    fig.update_traces(
        textinfo='label+value',
        textfont=dict(size=16)  # Adjust font size for better visibility
    )
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),  # Adjust margins to fit the treemap better
        legend_title_text='Current Status'  # Set the legend title
    )
    st.plotly_chart(fig)


###MAP

# Data for districts
data = {
    'District': ['Bugesera', 'Burera', 'Gasabo', 'Huye', 'Kamonyi', 'Karongi', 'Kicukiro', 'Muhanga', 
                 'Musanze', 'Nyamagabe', 'Nyamasheke', 'Nyarugenge', 'Rubavu', 'Ruhango', 'Rulindo', 
                 'Rusizi', 'Rwamagana'],
    'Lat': [-2.23988, -1.48351, -1.88294, -2.53487, -2.00987, -2.15078, -1.9992, -1.942, 
            -1.47941, -2.41583, -2.38224, -1.95604, -1.6827, -2.23296, -1.73413, -2.59792, -1.95066],
    'Long': [30.16991, 29.831, 30.14614, 29.6886, 29.90104, 29.41478, 30.14127, 29.72787, 
             29.6235, 29.48802, 29.18737, 30.06526, 29.28743, 29.78123, 29.9973, 28.96717, 30.43767]
}

# Create DataFrame


# Actual data provided
actual_data = """Rubavu Kicukiro Rubavu Rubavu Rubavu Rubavu Nyamasheke Rubavu Rusizi Rubavu Rubavu Gasabo Gasabo Gasabo Ruhango Nyarugenge Muhanga Nyarugenge Kicukiro Kicukiro Nyarugenge Bugesera Gasabo Ruhango Huye Karongi Gasabo Gasabo Nyarugenge Burera Burera Burera Gasabo Nyarugenge Nyarugenge Rubavu Rubavu Rubavu Rubavu Rubavu Rusizi Gasabo Kicukiro Gasabo Kicukiro Gasabo Rulindo Gasabo Kicukiro Kicukiro Musanze Kicukiro Nyamagabe Kicukiro Gasabo Nyarugenge Rwamagana Kicukiro Gasabo Kicukiro Kicukiro Kamonyi Nyarugenge Nyarugenge Kicukiro Kicukiro Gasabo Bugesera Gasabo Kicukiro Nyarugenge Kicukiro"""

# Count occurrences of each district
district_counts = Counter(actual_data.split())

# Add cases to the DataFrame
df['Cases'] = df['District'].map(district_counts).fillna(0)

# Ensure 'Cases' column is integer type
df['Cases'] = df['Cases'].astype(int)

# Add a small constant to all case numbers to ensure visibility
df['Cases_adjusted'] = df['Cases'] + 1

# Streamlit app
st.title('Mpox Cases Distribution in Rwanda')

# Create the map
fig = px.scatter_mapbox(df, 
                        lat='Lat', 
                        lon='Long', 
                        size='Cases_adjusted',
                        color='Cases',
                        hover_name='District', 
                        hover_data=['Cases'],
                        size_max=30,  # Reduced maximum dot size
                        zoom=7.5, 
                        center=dict(lat=-1.94, lon=29.87),
                        mapbox_style="open-street-map",
                        color_continuous_scale=[(0, 'violet'), (1, 'darkred')])  # Custom color scale
                        

# Update layout for better visibility and increased height
fig.update_layout(
    mapbox_style="open-street-map",
    height=800,  # Increased height of the figure
    margin={"r":0,"t":50,"l":0,"b":0}
)

# Update traces to reduce dot size
fig.update_traces(marker=dict(sizemin=2))  # Set minimum dot size

# Display the map in Streamlit
st.plotly_chart(fig, use_container_width=True)
