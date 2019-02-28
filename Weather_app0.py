
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,and_

from flask import Flask, jsonify
import json

import datetime as dt
from dateutil.relativedelta import relativedelta


#we assume the current time is 2017-08-23, the latest date for which our 
# weather dataset has records.
last_date_dataset="2017-08-23" 

current_time= (dt.datetime.strptime(last_date_dataset, '%Y-%m-%d')).strftime("%Y-%m-%d")
One_yrs_ago=(dt.datetime.strptime(last_date_dataset, '%Y-%m-%d')\
             - relativedelta(years=1)).strftime("%Y-%m-%d")
current_time
One_yrs_ago

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
    return ("""Welcome to my 'Home' page. Choose one of the following \
    routes to get weather data. The format of date variables, i.e, data, start,end should be in the canonical 
    form, e.g, 2017-01-02. The latest data is 2017-08-23 and the 
    earliest date being '2010-01-01'. Furthermore, Date should be within 12 months before  2017-08-23.<br/> """
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation/date<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs/past_year<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>")


# 4. Define what to do when a user hits the /about routes
@app.route("/api/v1.0/precipitation/<date>")
def Tobs_given_day(date):
    """Query for the dates and temperature observations 
    from the past 12 month from 2017-08-23.
Convert the query results to a Dictionary using date as the 
key and tobs as the value.
Return the JSON representation of your dictionary"""

    results = session.query(Measurement.date,Measurement.tobs).\
filter(Measurement.date.between(One_yrs_ago,current_time)).\
filter(func.strftime("%Y-%m-%d",Measurement.date)==date).all()
    
    results1=[results[i][1] for i in range(len(results))]
    results={results[0][0]:results1}
    print(f"Route /api/v1.0/precipitation/<date> with <date>={date} is being visited")
    return jsonify(results)
     


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    results = session.query(Station.station,Station.name).all()
    key=[results[i][0] for i in range(len(results))]
    values=[results[i][1] for i in range(len(results))]
    results=dict(zip(key,values))
    print(f"Route /api/v1.0/stations is being visited")
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
    print(f"Route  /api/v1.0/tobs/past_year is being visited")
    return jsonify(last_year_tobs)
    
    
@app.route("/api/v1.0/<start>")
def Tobs_from_satrt(start):
    results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
filter(Measurement.date>=start).group_by(Measurement.date).all()
    t_min=min([results[i][0] for i in range(len(results))])
    t_avg=sum([results[i][1] for i in range(len(results))])/len(results)
    t_max=max([results[i][2] for i in range(len(results))])
    print(f"Route /api/v1.0/<start> with <start>={start} is being visited")
    return jsonify({'T_min':t_min,'T_avg':t_avg,'T_max':t_max})

@app.route("/api/v1.0/<start>/<end>")
def Tobs_from_satrt_end(start,end):
    results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
filter(and_(Measurement.date>=start,Measurement.date<=end)).group_by(Measurement.date).all()
    t_min=min([results[i][0] for i in range(len(results))])
    t_avg=sum([results[i][1] for i in range(len(results))])/len(results)
    t_max=max([results[i][2] for i in range(len(results))])
    print(f"Route /api/v1.0/<start> with <start>={start} and <end>={end} is being visited")
    return jsonify({'T_min':t_min,'T_avg':t_avg,'T_max':t_max})    


if __name__ == "__main__":
    app.run(debug=True)
