#Dependencies 
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

# create engine to hawaii.sqlite
database_path = "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup 
app = Flask(__name__)

# first_date = session.query(Measurement.date).order_by((Measurement.date)).limit(1).all()
# print(first_date[0][0])
# last_date = session.query(Measurement.date).order_by((Measurement.date).desc()).limit(1).all()
# print(last_date[0][0])
# last_12mnth = (dt.datetime.strptime(last_date[0][0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
# print(last_12mnth)
############################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"<h2>Welcome to the Climate APP!</h2><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<em>Type in a single date in the format of YYYY-MM-DD to see the min, avg, and max temperature on the date.</em><br/>"
        f"/api/v1.0/<start><br/>"
        f"<em>Type in a date range in the format of YYYY-MM-DD to see the min, avg, and max temperature for the range.</em><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
    
###############################################################
#Route for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation data"""
    # Query all date and prcp values
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    all_prcp = []
    for date, prcp in results:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        all_prcp.append(measurement_dict)

    return jsonify(all_prcp)

#Route for stations 
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return station data"""
    # Query all date and prcp values
    results = session.query(Station.name).distinct().all()
    station_list = list(np.ravel(results))
    #close the session
    session.close()

    #Return a list of all distinct stations 
    return jsonify(station_list)

#Route for tobs 
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    query_result = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).first()[0]
    most_recent_date = dt.date(int(query_result[0:4]),int(query_result[5:7]),int(query_result[8:]))
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).filter(Station.station == "USC00519281").all() 

    # tobs_list = []
    
    # for date, tobs in tobs_results: 
    #     tobs_dict = {}
    #     tobs_dict[date] = tobs
    #     tobs_list.append(tobs_dict)

    session.close()

    return jsonify(tobs_results)

# Route for start 
@app.route("/api/v1.0/<start>")
def stats(start):
    # Create our session (link) from Python to the DB
    session = Session(engine) 

    # start = session.query(Measurement.date).order_by(Measurement.date).first()[0]
    # end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    temperatures_start = list(np.ravel(results))
    session.close()

    return jsonify(temperatures_start)

#Route for start and end
@app.route("/api/v1.0/<start>/<end>")
def stats_2(start,end): 
    # Create our session (link) from Python to the DB
    session = Session(engine) 

    # start = session.query(Measurement.date).order_by(Measurement.date).first()[0]
    # end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()[0]
    temperatures_start_end = list(np.ravel(results))
    session.close()

    return jsonify(temperatures_start_end)
            
if __name__ == "__main__":
    app.run(debug=True)