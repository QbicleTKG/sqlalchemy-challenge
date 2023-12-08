# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<br/>"
        f"<br/>"
        f"As a special treat for being selected as my grader for this assignment, copy/paste this into your browser (https://youtu.be/dQw4w9WgXcQ?si=Ph7YV87LBMrjNjVR)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    yearlong_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= dt.date(2016, 8, 23)).all()
    session.close()
    
    year_data = []
    for date, prcp in yearlong_data:
        data = {}
        data["date"] = date
        data["prcp"] = prcp
        year_data.append(data)

    return jsonify(year_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Return a list of all stations from the data set
    stations = session.query(Station.station).all()
    # Close the Session
    session.close()
    # Jsonify the results
    station_data = list(np.ravel(stations))
    # Convert list into a dictionary
    dict = {
        "Output": "Results for Station Data",
        "Results": station_data
    }
    return jsonify(dict)

@app.route("/api/v1.0/tobs")
def temperatures():

    temp_data = session.query(measurement.date, measurement.tobs).filter(measurement.date >= '2016-08-23').filter(measurement.station == 'USC00519281').all()
    session.close()

    temps = list(np.ravel(temp_data))

    dict = {
        "Output": "Results for Temperature Data",
        "Results": temps
    }

    return jsonify(dict)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    # Convert start from string to datetime object
    start = dt.datetime.strptime(start, "%Y-%m-%d")

    # If the end date is provided, convert it from string to datetime object
    if end:
        end = dt.datetime.strptime(end, "%Y-%m-%d")

    # Build the query based on whether an end date is provided
    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).filter(measurement.date >= start).all()
    else:
        # calculate TMIN, TAVG, TMAX with start and stop
        results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # Close the session
    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results as a JSON
    return jsonify(temps=temps)
    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)



if __name__ == '__main__':
    app.run(debug=True)