#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt


# In[2]:


import numpy as np
import pandas as pd
import datetime as dt


# # Reflect Tables into SQLAlchemy ORM

# In[3]:


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# In[4]:


# create engine to hawaii.sqlite
engine = create_engine(f"sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()


# In[5]:


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Access the ORM classes
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[6]:


# View all of the classes that automap found
Base.classes.keys()


# In[7]:


# Save references to each table
table_references = {}
for table_name, table_class in Base.classes.items():
    table_references[table_name] = table_class


# In[8]:


# Create our session (link) from Python to the DB
session = Session(engine)


# # Exploratory Precipitation Analysis

# In[9]:


# Find the most recent date in the data set.
most_recent_date = session.query(func.max(Measurement.date)).scalar()
most_recent_date


# In[10]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# Starting from the most recent data point in the database. 

# Calculate the date one year from the last date in data set.
one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
dates = [result[0] for result in results]
precipitation = [result[1] for result in results]


# In[11]:


# Save the query results as a Pandas DataFrame and set the index to the date column
df = pd.DataFrame(results, columns=['date', 'prcp'])

# Set the index to the date column
df.set_index('date', inplace=True)

# Print the DataFrame
print(df)


# In[12]:


# Sort the dataframe by date
df_sorted = df.sort_values('date')

# Print the sorted DataFrame
df_sorted


# In[13]:


# Use Pandas Plotting with Matplotlib to plot the data
df.plot(figsize=(8, 4))
plt.xlabel('Date')
plt.ylabel('Inches')
plt.title('Precipitation Data - Last 12 Months')
plt.xticks(rotation=90)
plt.grid(True)
plt.show()


# In[14]:


# Use Pandas to calcualte the summary statistics for the precipitation data
summary_stats = df['prcp'].describe()

# Print the summary statistics
summary_stats


# # Exploratory Station Analysis

# In[15]:


# Design a query to calculate the total number stations in the dataset
total_stations = session.query(func.count(Station.station)).scalar()
total_stations


# In[16]:


# Design a query to find the most active stations (i.e. what stations have the most rows?)
# List the stations and the counts in descending order.
station_counts = session.query(Measurement.station, func.count(Measurement.station)).    group_by(Measurement.station).    order_by(func.count(Measurement.station).desc()).all()

# Print the stations and counts
for station, count in station_counts:
    print(f"Station: {station}, Count: {count}")


# In[19]:


most_active_station_id = station_counts[0][0]


# In[23]:


# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
temperature_stats = session.query(func.min(Measurement.tobs).label('min_temp'),
                                 func.max(Measurement.tobs).label('max_temp'),
                                 func.avg(Measurement.tobs).label('avg_temp')).\
    filter(Measurement.station == most_active_station_id).first()

lowest_temp = temperature_stats.min_temp
highest_temp = temperature_stats.max_temp
avg_temp = temperature_stats.avg_temp


# In[30]:


# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
one_year_temp = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

temperature_observations = session.query(Measurement.tobs).    filter(Measurement.station == most_active_station_id).    filter(Measurement.date >= one_year_ago).all()

temperatures = [result[0] for result in temperature_observations]


# In[35]:


plt.hist(temperatures, bins=12)
plt.xlabel('Temperature')
plt.ylabel('Frequency')
plt.title(f'Temperature Observations for Station {most_active_station_id}\n')
plt.show()


# # Close session

# In[36]:


# Close Session
session.close()


# In[ ]:




