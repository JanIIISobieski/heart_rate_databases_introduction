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
        text = ''.join('Added heart rate of ', str(r['heart_rate']),
                       ' to ', r['user_email'])
    else:
        main.create_user(r['user_email'],
                         r['user_age'],
                         r['heart_rate'],
                         datetime.datetime.now())
        text = ''.join('Created user ', r['user_email'],
                       ' and initialized with HR ', str(r['heart_rate']))
    return jsonify({'info': text})


def is_subject_in_db(email):
    try:
        models.User.objects.raw({"_id": email}).first()
        user_exists = True
    except errors.DoesNotExist:
        user_exists = False
    return user_exists


@app.route('/api/heart_rate/<user_email>', methods=['GET'])
def get_user_heart_rates(user_email):
    if is_subject_in_db(user_email):
        wanted_user = models.User.objects.raw({'_id': user_email}).first()
        return jsonify({'heart_rate': wanted_user.heart_rate})
    else:
        return jsonify({'error': 'User not in database'})


@app.route('/api/heart_rate/average/<user_email>', methods=['GET'])
def get_avg_heart_rates(user_email):
    from numpy import mean
    if is_subject_in_db(user_email):
        wanted_user = models.User.objects.raw({'_id': user_email}).first()
        return jsonify({'avg_heart_rate': mean(wanted_user.heart_rate)})
    else:
        return jsonify({'error': 'User not in database'})


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
                        'tachycardic': tachy_flag})
    else:
        return jsonify({'error': 'User not in database'})


def is_tachycardic(age, u_heart_rate):
    from numpy import array
    tachy_dict = {0: 159,
                  3/365: 166,
                  7/365: 182,
                  30/365: 179,
                  90/365: 186,
                  180/365: 169,
                  1: 151,
                  3: 137,
                  5: 133,
                  8: 142,
                  12: 119,
                  15: 100}  # lower age cutoffs for defining tachycardia

    tachy_keys = array(list(tachy_dict.keys()))
    tachy_cutoff = tachy_dict[tachy_keys[tachy_keys < age][-1]]
    return str(u_heart_rate > tachy_cutoff)
