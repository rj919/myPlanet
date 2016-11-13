__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

# add configs to namespace
from labpack.records.settings import load_settings
telegram_config = load_settings('../cred/telegram.yaml')
moves_config = load_settings('../cred/moves.yaml')
planetos_config = load_settings('../cred/planetos.yaml')
token_config = load_settings('../data/moves-token.yaml')
update_path = '../data/telegram-update.yaml'

from time import time

job_list = [
    {
        'id': 'unittest.%s' % str(time()),
        'function': 'launch:app.logger.debug',
        'kwargs': { 'msg': 'Scheduler interval job is working.' },
        'interval': 2,
        'end': time() + 7
    },
    {
        'id': 'telegram.monitor.%s' % str(time()),
        'function': 'launch:monitor_telegram',
        'kwargs': { 'telegram_config': telegram_config, 'update_path': update_path },
        'interval': 2,
        'end': time() + 60 * 120
    },
    {
        'id': 'moves.monitor.%s' % str(time()),
        'function': 'launch:monitor_moves',
        'kwargs': { 'access_token': token_config['access_token'], 'service_scope': token_config['service_scope'], 'contact_id': token_config['contact_id'] },
        'interval': 60 * 5,
        'end': time() + 60 * 120
    },
    {
        'id': 'planetos.monitor.%s' % str(time()),
        'function': 'launch:monitor_planetos',
        'kwargs': { 'planetos_config': planetos_config, 'contact_id': token_config['contact_id'] },
        'interval': 60 * 5,
        'end': time() + 60 * 120
    },
    {
        'id': 'unittest.%s' % str(time()),
        'function': 'launch:app.logger.debug',
        'kwargs': { 'msg': 'Jobs completed.' },
        'dt': time() + 60 * 120 + 1
    }
]

if __name__ == '__main__':
    scheduler_url = 'http://localhost:5001'
    from labpack.platforms.apscheduler import apschedulerClient
    scheduler_client = apschedulerClient(scheduler_url)
    assert scheduler_client.get_info()['running']
    for job in job_list:
        if 'interval' in job.keys():
            response = scheduler_client.add_interval_job(**job)
            if 'error_message' in response.keys():
                print(response['error_message'])
        elif 'dt' in job.keys():
            response = scheduler_client.add_date_job(**job)
            if 'error_message' in response.keys():
                print(response['error_message'])
