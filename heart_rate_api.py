from flask import Flask, jsonify, request
from pymodm import errors, connect
import models
import datetime
import main

app = Flask(__name__)
connect("mongodb://vcm-3602.vm.duke.edu:27017/heart_rate_app")


@app.route('/api/heart_rate', methods=['POST'])
def post_heart_rate():
    r = request.get_json()
    print(r)
    if is_subject_in_db(r['user_email']):  # if subject already exists
        main.add_heart_rate(r['user_email'],
                            r['heart_rate'],
                            datetime.datetime.now())
        text = 'Heart rate added'
    else:
        main.create_user(r['user_email'],
                         r['user_age'],
                         r['heart_rate'],
                         datetime.datetime.now())
        text = 'New user created'
    return jsonify({'info': text}).status_code(201)


def is_subject_in_db(email):
    try:
        models.User.objects.raw({'_id': email}).first()
        user_exists = True
    except errors.DoesNotExist:
        user_exists = False
    return user_exists


@app.route('/api/heart_rate/<user_email>', methods=['GET'])
def get_user_heart_rates(user_email):
    if is_subject_in_db(user_email):
        wanted_user = models.User.objects.raw({'_id': user_email}).first()
        return jsonify({'heart_rate': wanted_user.heart_rate}).status_code(200)
    else:
        return jsonify({'error': 'User not in database'}).status_code(404)


@app.route('/api/heart_rate/average/<user_email>', methods=['GET'])
def get_avg_heart_rates(user_email):
    from numpy import mean
    if is_subject_in_db(user_email):
        wanted_user = models.User.objects.raw({'_id': user_email}).first()
        return jsonify({'avg_heart_rate': mean(wanted_user.heart_rate)}).status_code(200)
    else:
        return jsonify({'error': 'User not in database'}).status_code(404)


@app.route('/api/heart_rate/interval_average', methods=['POST'])
def get_int_average():
    from numpy import array, mean
    r = request.get_json()
    print(r)

    datetime_format = '%Y-%m-%d %H:%M:%S.%f'
    cutoff_date = datetime.datetime.strptime(r['heart_rate_average_since'],
                                             datetime_format)
    if is_subject_in_db(r['user_email']):
        wanted_user = models.User.objects.raw({'_id': r['user_email']}).first()
        heart_times = array(wanted_user.heart_rate_times)
        heart_rates = array(wanted_user.heart_rate)
        mean_heart_rate = mean(heart_rates[heart_times > cutoff_date])

        tachy_flag = is_tachycardic(wanted_user.age, mean_heart_rate)

        return jsonify({'avg_heart_rate_since_date': mean_heart_rate,
                        'tachycardic': str(tachy_flag[0])}).status_code(200)
    else:
        return jsonify({'error': 'User not in database'}).status_code(404)


def is_tachycardic(age, mean_heart_rate):
    from numpy import array
    tachy_dict = {1: 151,
                  3: 137,
                  5: 133,
                  8: 142,
                  12: 119,
                  15: 100}  # lower age cutoffs for defining tachycardia

    tachy_keys = array(list(tachy_dict.keys()))
    tachy_cutoff = tachy_dict[tachy_keys[tachy_keys < age][-1]]
    return (mean_heart_rate > tachy_cutoff, tachy_cutoff)
