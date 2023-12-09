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
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # get data and close session
    yearlong_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= dt.date(2016, 8, 23)).all()
    session.close()
    # jsonify data
    year_data = []
    for date, prcp in yearlong_data:
        data = {}
        data["date"] = date
        data["prcp"] = prcp
        year_data.append(data)

    return jsonify(year_data)

@app.route("/api/v1.0/stations")
def stations():
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
    # get data and close session
    temp_data = session.query(measurement.date, measurement.tobs).filter(measurement.date >= '2016-08-23').filter(measurement.station == 'USC00519281').all()
    session.close()
    # jsonify data
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
    # get data and close session
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
        # Convert start and end dates from string to datetime objects
    start = dt.datetime.strptime(start, "%m%d%Y")
    if end:
        end = dt.datetime.strptime(end, "%m%d%Y")
        # calculate TMIN, TAVG, TMAX for dates between start and end
        results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    else:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).filter(measurement.date >= start).all()
    # Close the session
    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    # Return the results as a JSON
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)