from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date

# Create the Flask application instance
app = Flask(__name__)

# Set up the SQLAlchemy engine and session
engine = create_engine("sqlite:///path/to/your_database.db")
Base = declarative_base(bind=engine)

class Measurement(Base):
    __tablename__ = "measurement"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    prcp = Column(Float)
    # Add other columns as per your actual data

class Station(Base):
    __tablename__ = "station"
    id = Column(Integer, primary_key=True)
    station = Column(String)
    # Add other columns as per your actual data

Base.metadata.create_all()

session = Session(bind=engine)

# Define the routes
@app.route("/")
def home():
    # List all the available routes
    routes = [
        "/api/v1.0/precipitation",
        "/api/v1.0/stations",
        "/api/v1.0/tobs",
        "/api/v1.0/<start>",
        "/api/v1.0/<start>/<end>",
    ]
    return jsonify(routes)

@app.route("/api/v1.0/stations")
def stations():
    # Retrieve the list of stations from the dataset
    station_data = session.query(Station.station).all()
    session.close()

    stations_list = [station[0] for station in station_data]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Retrieve the most active station
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count().desc())
        .first()
    )

    # Calculate the date range for the previous year
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
    one_year_ago = last_date - timedelta(days=365)

    # Query the temperature observations for the previous year from the most active station
    tobs_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station[0])
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    session.close()

    # Create a list of dictionaries containing the date and temperature observations
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    # Calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    start_date = datetime.strptime(start, "%Y-%m-%d").date()

    temperature_data = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start_date)
        .all()
    )
    session.close()

    temperature_list = [
        {"TMIN": temp[0], "TAVG": temp[1], "TMAX": temp[2]} for temp in temperature_data
    ]
    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    # Calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()

    temperature_data = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start_date)
        .filter(Measurement.date <= end_date)
        .all()
    )
    session.close()

    temperature_list = [
        {"TMIN": temp[0], "TAVG": temp[1], "TMAX": temp[2]} for temp in temperature_data
    ]
    return jsonify(temperature_list)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results from your precipitation analysis to a dictionary
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
    one_year_ago = last_date - timedelta(days=365)
    prcp_data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    session.close()

    prcp_dict = {date: prcp for date, prcp in prcp_data}
    return jsonify(prcp_dict)

# Run the Flask application
if __name__
