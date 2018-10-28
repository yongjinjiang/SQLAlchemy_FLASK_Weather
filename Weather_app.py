
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import json

import datetime as dt
from dateutil.relativedelta import relativedelta


#we assume the current time is now-1 year.
#If we choose now, there is no data in the past 12 months
# current_time= (dt.datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d")
# One_yrs_ago=(dt.datetime.now() - relativedelta(years=2)).strftime("%Y-%m-%d")
current_time= ("2017-08-23" - relativedelta(years=1)).strftime("%Y-%m-%d")
One_yrs_ago=("2017-08-23" - relativedelta(years=2)).strftime("%Y-%m-%d")

engine = create_engine("""sqlite:///Resources/hawaii.sqlite""")
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Welcome to my 'Home' page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation/<date><br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs/past_year<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>")


# 4. Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation/<date>")
def Tobs_given_day(date):
    """Query for the dates and temperature observations 
    from the last year.
Convert the query results to a Dictionary using date as the 
key and tobs as the value.
Return the JSON representation of your dictionary"""
    
    results = session.query(Measurement.date,Measurement.tobs).\
filter(Measurement.date.between(One_yrs_ago,current_time)).\
filter(func.strftime("%m-%d",Measurement.date)==date).all()
    
    results1=[results[i][1] for i in range(len(results))]
    results={results[0][0]:results1}
    return jsonify(results)
     


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    results = session.query(Station.station,Station.name).all()
    key=[results[i][0] for i in range(len(results))]
    values=[results[i][1] for i in range(len(results))]
    results=dict(zip(key,values))
    return jsonify(results)

@app.route("/api/v1.0/tobs/past_year")
def Tobs_past_year():
    """Return a JSON list of Temperature Observations (tobs) for the previous year""" 
    results = pd.DataFrame(session.query(Measurement.date,Measurement.tobs).\
filter(Measurement.date.between(One_yrs_ago,current_time)).all());

    dates_of_last_year=list(results.sort_values(by='date')['date'].unique())  
    aa1=results.sort_values(by='date').groupby('date')
    last_year_tobs={dates_of_last_year[i]:list(aa1.get_group(dates_of_last_year[i])['tobs'])\
                    for i in range(len(aa1))}
    return jsonify(last_year_tobs)
    
    
@app.route("/api/v1.0/<start>")
def Tobs_from_satrt(start):
    results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
filter(Measurement.date>=start).group_by(Measurement.date).all()
    t_min=min([results[i][0] for i in range(len(results))])
    t_avg=sum([results[i][1] for i in range(len(results))])/len(results)
    t_max=max([results[i][2] for i in range(len(results))])
    return jsonify({'T_min':t_min,'T_avg':t_avg,'T_max':t_max})

@app.route("/api/v1.0/<start>/<end>")
def Tobs_from_satrt_end(start,end):
    results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
filter(_and(Measurement.date>=start,Measurement.date<=end)).group_by(Measurement.date).all()
    t_min=min([results[i][0] for i in range(len(results))])
    t_avg=sum([results[i][1] for i in range(len(results))])/len(results)
    t_max=max([results[i][2] for i in range(len(results))])
    return jsonify({'T_min':t_min,'T_avg':t_avg,'T_max':t_max})    


if __name__ == "__main__":
    app.run(debug=True)
