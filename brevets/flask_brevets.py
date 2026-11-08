"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times for one control, using rules
    described at https://rusa.org/octime_alg.html.
    Expects URL-encoded arguments:
      km: control distance in kilometers
      brevet_dist_km: nominal brevet distance (200/300/400/600/1000)
      begin_date: YYYY-MM-DD, begin_time: HH:mm (brevet start)
    Returns {"result": {"open", "close"}} or {"error": message}.
    """
    app.logger.debug("Got a JSON request")
    app.logger.debug("request.args: {}".format(request.args))
    km = request.args.get('km', type=float)
    brevet_dist_km = request.args.get('brevet_dist_km', 200, type=int)
    begin_date = request.args.get('begin_date', '2017-01-01')
    begin_time = request.args.get('begin_time', '00:00')
    if km is None:
        return flask.jsonify(error="Distance must be a number")
    try:
        start = arrow.get("{} {}".format(begin_date, begin_time),
                          "YYYY-MM-DD HH:mm").isoformat()
    except (arrow.parser.ParserError, ValueError):
        return flask.jsonify(error="Invalid start date/time")
    try:
        open_time = acp_times.open_time(km, brevet_dist_km, start)
        close_time = acp_times.close_time(km, brevet_dist_km, start)
    except ValueError as e:
        return flask.jsonify(error=str(e))
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
