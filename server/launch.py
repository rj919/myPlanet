__author__ = 'rcj1492'
__created__ = '2015.10'
__license__ = 'MIT'

# initialize app and scheduler objects
from server.init import app, ap_scheduler
from flask import request, session, jsonify, url_for, render_template

# construct the landing page
from labpack.records.settings import load_settings
api_model = load_settings('models/api-model.json')
@app.route('/')
def landing_page():
    return jsonify(api_model['schema']), 200

# construct the catchall for URLs which do not exist
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# construct scheduler configs
scheduler_configs = {
    'SCHEDULER_JOBS': [ {
        'id': 'app.logger.debug.start',
        'func': 'init:app.logger.debug',
        'kwargs': { 'msg': 'APScheduler has started.' },
        'misfire_grace_time': 5,
        'max_instances': 1,
        'replace_existing': True,
        'coalesce': True
    } ],
    'SCHEDULER_TIMEZONE': 'UTC',
    'SCHEDULER_VIEWS_ENABLED': True
}

# add jobs to pre-scheduled jobs
from server.jobs import job_list
from labpack.platforms.apscheduler import apschedulerClient
scheduler_client = apschedulerClient('http://localhost:5001')
for job in job_list:
    job_fields = scheduler_client._construct_fields(**job)
    standard_fields = {
        'misfire_grace_time': 5,
        'max_instances': 1,
        'replace_existing': True,
        'coalesce': True
    }
    job_fields.update(**standard_fields)
    scheduler_configs['SCHEDULER_JOBS'].append(job_fields)

# add scheduler configurations to app configs
app.config.update(**scheduler_configs)

# attach app to scheduler and start scheduler
ap_scheduler.init_app(app)
ap_scheduler.start()

# initialize test wsgi localhost server with default memory job store
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    http_server.serve_forever()
    # app.run(host='0.0.0.0', port=5001)
