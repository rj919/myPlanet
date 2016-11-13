__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

def retrieve_location_data(contact_id):

    from labpack.records.time import labDT
    from labpack.storage.appdata import appdataClient
    moves_data_client = appdataClient('Moves', prod_name='myPlanet')
    contact_filter = [{0: {'discrete_values': [contact_id]}}]
    filter_function = moves_data_client.conditionalFilter(contact_filter)
    moves_data_list = moves_data_client.list(filter_function=filter_function, reverse_search=True)
    moves_data_record = {}
    location_data = {
        'longitude': 0.0,
        'latitude': 0.0,
        'dt': 0.0
    }
    if moves_data_list:
        moves_data_key = moves_data_list[0]
        moves_data_record = moves_data_client.read(moves_data_key)
    if 'segments' in moves_data_record.keys():
        if moves_data_record['segments']:
            last_segment = moves_data_record['segments'][-1]
            location_data['longitude'] = last_segment['place']['location']['lon']
            location_data['latitude'] = last_segment['place']['location']['lat']
            location_data['dt'] = labDT.fromISO(last_segment['endTime']).epoch()

    return location_data

def retrieve_planet_data(contact_id):

    from labpack.storage.appdata import appdataClient
    planet_data_client = appdataClient('Planet OS', prod_name='myPlanet')
    planetos_datasets = {
        'ozone': 'OZCON_1sigmalevel',
        'particulate': 'PMTF_1sigmalevel'
    }
    planet_data = {
        'ozone': 0.0,
        'particulate': 0.0
    }
    for key, value in planetos_datasets.items():
        contact_filter = [
            {0: {'discrete_values': [contact_id]}, 1: {'discrete_values': [key]}}
        ]
        filter_function = planet_data_client.conditionalFilter(contact_filter)
        planet_data_list = planet_data_client.list(filter_function=filter_function, reverse_search=True)
        planet_data_record = {}
        if planet_data_list:
            planet_data_key = planet_data_list[0]
            planet_data_record = planet_data_client.read(planet_data_key)
        if 'entries' in planet_data_record.keys():
            if planet_data_record['entries']:
                last_entry = planet_data_record['entries'][-1]
                planet_data[key] = last_entry['data'][value]

    return planet_data

def monitor_telegram(telegram_config, update_path):

    from labpack.messaging.telegram import telegramBotClient
    init_kwargs = {
        'access_token': telegram_config['telegram_access_token'],
        'bot_id': telegram_config['telegram_bot_id']
    }
    admin_id = 'telegram_%s' % telegram_config['telegram_admin_id']
    telegram_client = telegramBotClient(**init_kwargs)
    from labpack.records.settings import load_settings, save_settings
    update_record = load_settings(update_path)
    last_update = update_record['last_update']
    updates_details = telegram_client.get_updates(last_update)
    update_list = []
    if updates_details['json']['result']:
        update_list = sorted(updates_details['json']['result'], key=lambda k: k['update_id'])
        offset_details = { 'last_update': update_list[-1]['update_id']}
        save_settings(offset_details, update_path, overwrite=True)
    for update in update_list:
        user_id = update['message']['from']['id']
        contact_id = 'telegram_%s' % user_id
        text_tokens = []
        if 'text' in update['message'].keys():
            text_tokens = update['message']['text'].split()
        keywords = [ 'air', 'particulate', 'ozone', 'quality']
        keyword_found = False
        for token in text_tokens:
            if token.lower() in keywords:
                keyword_found = True
                break
        if keyword_found:
            context_details = {}
            if contact_id == admin_id:
                location_data = retrieve_location_data(contact_id)
                context_details.update(location_data)
                planet_data = retrieve_planet_data(contact_id)
                context_details.update(planet_data)
                telegram_client.send_message(user_id, str(context_details))

    return True

def monitor_moves(access_token, service_scope, contact_id):

    from time import time
    from labpack.storage.appdata import appdataClient
    moves_data_client = appdataClient('Moves', prod_name='myPlanet')
    from labpack.activity.moves import movesClient
    moves_client = movesClient(access_token, service_scope)
    end_time = time()
    start_time = time() - 60 * 60
    profile_details = moves_client.get_profile()
    places_kwargs = {
        'timezone_offset': profile_details['json']['profile']['currentTimeZone']['offset'],
        'first_date': profile_details['json']['profile']['firstDate'],
        'start': start_time,
        'end': end_time
    }
    places_details = moves_client.get_places(**places_kwargs)
    key_string = '%s/%s.json' % (contact_id, str(time()))
    moves_data_client.create(key_string, places_details['json'][0])

    return True

def monitor_planetos(planetos_config, contact_id):

    from labpack.storage.appdata import appdataClient
    planet_data_client = appdataClient('Planet OS', prod_name='myPlanet')
    location_details = retrieve_location_data(contact_id)
    planetos_datasets = {
        'ozone': 'noaa_aqfs_avg_1h_o3_conus',
        'particulate': 'noaa_aqfs_pm25_bc_conus'
    }
    planetos_endpoint = 'http://api.planetos.com/v1/datasets/'
    if location_details['latitude'] and location_details['longitude']:
        import requests
        from time import time
        for key, value in planetos_datasets.items():
            query_fields = {
                'origin': 'dataset-details',
                'lat': location_details['latitude'],
                'lon': location_details['longitude'],
                'apikey': planetos_config['planetos_api_key']
            }
            url = '%s%s/point' % (planetos_endpoint, value)
            response = requests.get(url=url, params=query_fields)
            planetos_record = response.json()
            key_string = '%s/%s/%s.json' % (contact_id, key, str(time()))
            planet_data_client.create(key_string, planetos_record)

    return True

if __name__ == '__main__':
    from labpack.records.settings import load_settings
    telegram_config = load_settings('../cred/telegram.yaml')
    moves_config = load_settings('../cred/moves.yaml')
    planetos_config = load_settings('../cred/planetos.yaml')
    token_config = load_settings('../data/moves-token.yaml')
    update_path = '../data/telegram-update.yaml'
    monitor_telegram(telegram_config, update_path)
    # monitor_moves(token_config['access_token'], token_config['service_scope'], token_config['contact_id'])
    # monitor_planetos(planetos_config, token_config['contact_id'])
    # planet_data = retrieve_planet_data(token_config['contact_id'])
    # print(telegram_config)