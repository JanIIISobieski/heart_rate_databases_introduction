import requests
import datetime
from time import sleep

def main():
    r1 = requests.post('http://127.0.0.1:5000/api/heart_rate',
                       json={'user_email': 'iamemail@email.com',
                             'user_age': 100,
                             'heart_rate': 73})
    print(r1.text)

    sleep(2)

    cutoff_time = datetime.datetime.now()
    datetime_format = '%Y-%m-%d %H:%M:%S.%f'
    cutoff_time_str = cutoff_time.strftime(datetime_format)

    r2 = requests.post('http://127.0.0.1:5000/api/heart_rate',
                       json={'user_email': 'suyash@suyashkumar.com',
                             'user_age': 24,
                             'heart_rate': 70})
    print(r2.text)

    sleep(2)

    r3 = requests.get('http://127.0.0.1:5000/api/heart_rate/iamemail@email.com')
    print(r3.text)

    sleep(2)

    r4 = requests.get('http://127.0.0.1:5000/api/heart_rate/iamemail2@email.com')
    print(r4.text)

    sleep(2)

    r5 = requests.get('http://127.0.0.1:5000/api/heart_rate/average/suyash@suyashkumar.com')
    print(r5.text)

    sleep(2)

    r6 = requests.get('http://127.0.0.1:5000/api/heart_rate/average/iamemail@email.com')
    print(r6.text)

    sleep(2)

    r7 = requests.post('http://127.0.0.1:5000/api/heart_rate/interval_average',
                       json={'user_email': 'suyash@suyashkumar.com',
                             'heart_rate_average_since': cutoff_time_str})
    print(r7.text)

    sleep(2)

    r8 = requests.post('http://127.0.0.1:5000/api/heart_rate',
                       json={'user_email': 'suyash@suyashkumar.com',
                             'user_age': 24,
                             'heart_rate': 72})
    print(r8.text)

    sleep(2)

    r9 = requests.post('http://127.0.0.1:5000/api/heart_rate/interval_average',
                       json={'user_email': 'suyash@suyashkumar.com',
                             'heart_rate_average_since': cutoff_time_str})
    print(r9.text)

if __name__ == '__main__':
    main()
