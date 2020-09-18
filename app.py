import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

## setup database first
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


## Flask Setup
app = Flask(__name__)

## flask routes
@app.route('/')
def home():
    return (
        f"Welcome to the Hawaii Climate Data Webpage<br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
#convert query results to a dictionary using date as the key and prcp as the value
#return a JSON rep of your dictionary

#calculate the date a year from the last date of the date
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#filter precip data by date constrictions
precip_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago).\
    order_by(Measurement.date).all()

#from stack overflow - list comprehension and dictionaries
#{key: value for (key, value) in iterable}
#create a dictionary using date as key and prcp as value
1yr_precip = {date: prcp for date, prcp in precip_data}

@app.route("/api/v1.0/stations")
#return json list of stations in the dataset

@app.route("/api/v1.0/tobs")
#query dates for last year of data
#query for most active station
#return a json list of temp obs for last year of data

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
#return json of min, max, avg temp
#given start only calc TMIN,TAVG,TMAX for all dates greater than or equal to date
#given start and end, calculate TMIN, TAVG, TMAX for dates in between and inclusive
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

   