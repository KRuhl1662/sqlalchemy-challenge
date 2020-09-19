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
        f"/api/v1.0/temp/start/end, need at least start date, use format Y-m-d/Y-m-d"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #convert query results to a dictionary using date as the key and prcp as the value
    #return a JSON rep of your dictionary

    #calculate the date a year from the last date of the date
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #filter precip data by date constrictions
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()

    #close session
    session.close()

    #from stack overflow - list comprehension and dictionaries
    #{key: value for (key, value) in iterable}
    #create a dictionary using date as key and prcp as value

    yr_precip = {date: prcp for date, prcp in precip_data}
    return jsonify(yr_precip)

@app.route("/api/v1.0/stations")
def stations():
    #return json list of stations in the dataset
    all_stations = session.query(Station.station).all()

    #close session
    session.close()

    #one way to return a jsonify list
    station_result =[s[0] for s in all_stations]

    return jsonify(station_result)



@app.route("/api/v1.0/tobs")
def temp_monthly():
    #query dates for last year of data
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #query for most active station (queried most overall active station, not most active in last year)
    station_query = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    #close session
    session.close()

    station_result =[s[0] for s in station_query[:1]]
    station_id = station_result[0][:11]
    
    #return a json list of temp obs for last year of data
    temp_for_station = session.query(Measurement.tobs).filter(Measurement.station == station_id).\
        filter(Measurement.date >= year_ago).all()

    #close session
    session.close()

    #another way to return jsonify list
    temp_result =list(np.ravel(temp_for_station))

    return jsonify(temp_result)
    

@app.route("/api/v1.0/temp/<start>")
def start_date(start):

    #take in user input date
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")

    #given start only calc TMIN,TAVG,TMAX for all dates greater than or equal to date
    start_summary = session.query(func.min(Measurement.tobs),func.round(func.avg(Measurement.tobs)),func.max(Measurement.tobs)).\
	filter(Measurement.date >= start_date).all()

    #close session
    session.close()

    #return json of min, max, avg temp
    single_stats = list(np.ravel(start_summary))
    return jsonify(single_stats)

# i know some of my classmates made this some sort of loop, but since we found the start above it seems redundant, and to be perfectly honest
# i couldn't get it to work if i just put in a start date for the part below (with the part above commented out. I have included the original
# loop written commented out after code is finished)

@app.route("/api/v1.0/temp/<start>/<end>")
def date_range(start=None, end=None):

    #take in user input
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    end_date = dt.datetime.strptime(end,"%Y-%m-%d")

    #select statment
    stats = [func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs)), func.max(Measurement.tobs)]


    # calculate TMIN, TAVG, TMAX with start and stop
    range_summary = session.query(*stats).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    #close session
    session.close()
    
    #return json of min, max, avg temp
    range_stats = list(np.ravel(range_summary))
    return jsonify(range_stats)
    

    
if __name__ == '__main__':

    app.run(port=9999)



 
   
# @app.route("/api/v1.0/temp/<start>/<end>")
# def date_range(start=None, end=None):

#     #take in user input
#     start_date = dt.datetime.strptime(start,"%Y-%m-%d")
#     end_date = dt.datetime.strptime(end,"%Y-%m-%d")

#     #select statment
#     stats = [func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs)), func.max(Measurement.tobs)]

#     if not end:
#         #given start only calc TMIN,TAVG,TMAX for all dates greater than or equal to date
#         start_summary = session.query(*stats).filter(Measurement.date >= start_date).all()

#         single_stats = list(np.ravel(start_summary))
#         return jsonify(single_stats)

#     # calculate TMIN, TAVG, TMAX with start and stop
#     range_summary = session.query(*stats).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

#     #return json of min, max, avg temp
#     range_stats = list(np.ravel(range_summary))
#     return jsonify(range_stats)
    
