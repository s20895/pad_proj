import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Data loading
df = pd.read_csv('apartments_pl_2024_04.csv')

# Data cleaning
df.drop(['condition', 'buildingMaterial'], axis=1, inplace=True)
df.dropna(axis=0, inplace=True)

numeric_columns = ['squareMeters', 'rooms', 'floor', 'floorCount', 'buildYear', 'centreDistance', 'poiCount', 
                   'schoolDistance', 'clinicDistance', 'postOfficeDistance', 'kindergartenDistance', 
                   'restaurantDistance', 'collegeDistance', 'pharmacyDistance', 'price']

df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)

categorical_columns = ['type', 'city', 'ownership', 'hasParkingSpace', 'hasBalcony', 'hasElevator', 
                       'hasSecurity', 'hasStorageRoom']

df[categorical_columns] = df[categorical_columns].astype(str)

binary_columns = ['hasParkingSpace', 'hasBalcony', 'hasElevator', 'hasSecurity', 'hasStorageRoom']
for col in binary_columns:
    df[col] = df[col].map({'yes': True, 'no': False})
    
df['pricePerSqM']=df['price']/df['squareMeters']
df['pricePerSqM']=df['pricePerSqM'].astype(int)

# Sidebar filters
st.set_page_config(layout="wide")
st.sidebar.title("Data filters")

# City selection
cities = df['city'].unique()
selected_city = st.sidebar.selectbox("Select a city", np.append(['All'], cities))

# Apartment type selection
apartment_types = df['type'].dropna().unique()
selected_type = st.sidebar.selectbox("Select an apartment type", np.append(['All'], apartment_types))

# Number of rooms selection
df['rooms'] = df['rooms'].fillna(0).astype(int)
rooms = df['rooms'].unique()
selected_rooms = st.sidebar.selectbox("Select number of rooms", np.append(['All'], np.sort(rooms)))

# Price range selection
min_price, max_price = int(df['price'].min()), int(df['price'].max())
selected_price = st.sidebar.slider("Select a price range [PLN]", min_price, max_price, (min_price, max_price))

# Area range selection
min_area, max_area = int(df['squareMeters'].min()), int(df['squareMeters'].max())
selected_area = st.sidebar.slider("Select an area [m2]", min_area, max_area, (min_area, max_area))

# Misc features selection
has_parking = st.sidebar.checkbox("Parking Space")
has_balcony = st.sidebar.checkbox("Balcony")
has_elevator = st.sidebar.checkbox("Elevator")
has_security = st.sidebar.checkbox("Security")
has_storage_room = st.sidebar.checkbox("Storage Room")

# Filter data based on selections
filtered_df = df
if selected_city != 'All':
    filtered_df = df[df['city'] == selected_city]
if selected_type != 'All':
    filtered_df = filtered_df[filtered_df['type'] == selected_type]
if selected_rooms != 'All':
    filtered_df = filtered_df[filtered_df['rooms'] == int(selected_rooms)]
filtered_df = filtered_df[(filtered_df['price'] >= selected_price[0]) & (filtered_df['price'] <= selected_price[1])]
filtered_df = filtered_df[(filtered_df['squareMeters'] >= selected_area[0]) & (filtered_df['squareMeters'] <= selected_area[1])]

if has_parking:
    filtered_df = filtered_df[filtered_df['hasParkingSpace'] == True]
if has_balcony:
    filtered_df = filtered_df[filtered_df['hasBalcony'] == True]
if has_elevator:
    filtered_df = filtered_df[filtered_df['hasElevator'] == True]
if has_security:
    filtered_df = filtered_df[filtered_df['hasSecurity'] == True]
if has_storage_room:
    filtered_df = filtered_df[filtered_df['hasStorageRoom'] == True]

# Main dashboard
st.title("Apartment Prices in Poland")

col1, col2 = st.columns(2)
with col1:
    # Summary statistics
    st.header("Summary Statistics")
    st.write(f"Total Listings: {filtered_df.shape[0]}")
    st.write(f"Average Size [sqm]: {filtered_df['squareMeters'].mean():.2f}")
    st.write(f"Average Price [PLN]: {filtered_df['price'].mean():.2f}")
    st.write(f"Median Price [PLN]: {filtered_df['price'].median():.2f}")

    # Price distribution
    st.header("Price Distribution")
    fig = px.histogram(filtered_df['price'], x='price', labels={'price':'Price [mil PLN]'}, nbins=20).update_layout(yaxis_title="Number of Apartments")
    st.plotly_chart(fig)
    
    # Apartment size distribution
    st.header("Apartment Area Distribution")
    fig = px.histogram(filtered_df['squareMeters'], x='squareMeters', labels={'squareMeters':'Apartment Size [sqm]'}, nbins=20).update_layout(yaxis_title="Number of Apartments")
    st.plotly_chart(fig)
      
    # Area vs price
    st.header("Apartment Area vs Price")
    fig = px.scatter(filtered_df, x="price", y="squareMeters", color='city', labels = {'price':'Price [PLN]', 'squareMeters':'Area [sqm]', 'city':'City'}, hover_name='id')
    fig.update_layout(height = 600)
    st.plotly_chart(fig,height = 600)
    
    # Build year vs price
    st.header("Build Year vs Price")
    fig = px.scatter(filtered_df, x="pricePerSqM", y="buildYear", color='city', labels = {'pricePerSqM':'Price Per Square Meter [PLN]', 'buildYear':'Build Year', 'city':'City'},  hover_name='id')
    fig.update_layout(height = 600)
    st.plotly_chart(fig,heigh = 600)
    
    # Price per sq m vs city
    st.header("Price Range per Location")
    fig = px.violin(filtered_df, x= 'pricePerSqM', y='city', labels = {'pricePerSqM':'Price Per Square Meter [PLN]', 'city':'City'}, box=True, points="all")
    fig.update_layout(height = 800)
    st.plotly_chart(fig,height = 800)
    
    # Build year distribution
    st.header("Build Year Distribution")
    fig = px.histogram(filtered_df['buildYear'], x="buildYear", labels = {'buildYear':'Build Year'}, nbins=20).update_layout(yaxis_title="Count")
    st.plotly_chart(fig)
    
    # Building year vs type of building
    st.header("Build Year vs Building Type")
    fig = px.histogram(filtered_df, x='buildYear', color='type', labels = {'buildYear':'Build Year', 'type':'Type of Building'}, nbins=20, barmode='overlay').update_layout(yaxis_title="Count")
    legendNames = {'blockOfFlats':'Block Of Flats', 'apartmentBuilding':'Apartment Building', 'tenement':'Tenement'}
    fig.for_each_trace(lambda t: t.update(name = legendNames[t.name]))
    st.plotly_chart(fig)

    # Filtered records
    st.header("Filtered Apartments")
    st.dataframe(filtered_df, use_container_width=True)
    
with col2:
    # Map of apartment locations
    st.header("Map of Apartment Locations")
    #st.map(filtered_df, latitude='latitude', longitude='longitude', size='price')    
    fig = px.density_mapbox(filtered_df, lat='latitude', lon='longitude', z='price' , radius=10, hover_name='id', hover_data=['price', 'squareMeters'], zoom=6)
    fig.update_layout(mapbox_style='carto-positron', margin={'r': 10, 't': 10, 'l': 10, 'b': 10}, height = 800)
    st.plotly_chart(fig, height = 800)
    
    # Distance from apartments to pois  
    poiTypes = ['school', 'clinic', 'postOffice', 'kindergarten', 'restaurant', 'college', 'pharmacy']
    
    for poi in poiTypes:
        st.header("Apartment distance to " + poi)
        fig = px.histogram(filtered_df[poi + 'Distance'], x=poi+'Distance', labels={poi+'Distance':'Distance to '+poi+' [km]'}, nbins=30).update_layout(yaxis_title="Count")
        st.plotly_chart(fig)