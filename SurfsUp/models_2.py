# coding: utf-8

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# create engine to hawaii.sqlite
engine = create_engine(f"sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Access the ORM classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
table_references = {}
for table_name, table_class in Base.classes.items():
    table_references[table_name] = table_class

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
most_recent_date = session.query(func.max(Measurement.date)).scalar()

# Design a query to retrieve the last 12 months of precipitation data and plot the results.
one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
dates = [result[0] for result in results]
precipitation = [result[1] for result in results]

# Save the query results as a Pandas DataFrame and set the index to the date column
df = pd.DataFrame(results, columns=['date', 'prcp'])
df.set_index('date', inplace=True)

# Sort the dataframe by date
df_sorted = df.sort_values('date')

# Use Pandas Plotting with Matplotlib to plot the data
df.plot(figsize=(8, 4))
plt.xlabel('Date')
plt.ylabel('Inches')
plt.title('Precipitation Data - Last 12 Months')
plt.xticks(rotation=90)
plt.grid(True)
plt.show()

# Use Pandas to calculate the summary statistics for the precipitation data
summary_stats = df['prcp'].describe()
print(summary_stats)

# Close session
session.close()
