from flask import Flask, jsonify, request
from pymodm import connect
import models
import datetime
import main

app = Flask(__name__)

@app.route('/api/heart_rate', methods=['POST'])
def post_heart_rate():
    r = request.get_json()
    print(r)
    if is_subject_in_db(r):  #if subject already exists
        main.add_heart_rate(r['user_email'],
                            r['heart_rate'],
                            datetime.datetime.now())  
        print('Added heart rate of ' + str(r['heart_rate']) + ' to ' + r['user_email'])
    else:
        main.create_user(r['user_email'],
                         r['user_age'],
                         r['heart_rate'],
                         datetime.datetime.now())
        print('Created user ' + r['user_email'] +
              ' and initialized with HR ' + r['heart_rate'])
    return 
        
def is_subject_in_db(json_file):
    user = models.User.objects.raw({"_id": json_file['user_email']}).first()
    return user.email == json_file('user_email')

@app.route('/api/heart_rate/<user_email>', methods=['GET'])
def get_user_heart_rates(user_email):
    wanted_user = models.User.objects.raw({'_id': user_email}).first()
    return jsonify({'heart_rate': wanted_user.heart_rate})

@app.route('/api/heart_rate/average/<user_email>', methods=['GET'])
def get_avg_heart_rates(user_email):
    from numpy import mean
    wanted_user = models.User.objects.raw({'_id': user_email}).first()
    return jsonify({'avg_heart_rate': mean(wanted_user.heart_rate)})

@app.route('/api/heart_rate/interval_average', methods=['POST'])
def get_int_average():
    from numpy import array, greater
    r = request.get_json()
    print(r)
    
    datetime_format = '%Y-%m-%d %H:%M:%S:%f'
    cutoff_date = datetime.datetime.strptime(r['heart_rate_average_since'],
                                             datetime_format)
    
    wanted_user = models.User.objects.raw({'_id': r['user_email']}).first()
    
    
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
                  15: 100}  #lower age cutoffs for defining tachycardia
    
    tachy_keys = array(list(tachy_dict.keys()))
    
    pass
    
    