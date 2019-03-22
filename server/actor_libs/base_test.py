from __future__ import division

import math
import uuid
import random
import string
import hashlib
import unittest
from datetime import datetime, timedelta
from random import choice, randint, randrange, uniform
from string import ascii_letters, digits

import requests

from app import create_app
from app.models import User


class TestCase(unittest.TestCase):
    api_url = 'http://127.0.0.1:7000/api/v1'
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
    }
    tenant_uid = None
    user_id = None

    def setUp(self):
        app = create_app()
        self._context = app.app_context()
        self._context.push()
        self.app = app
        self.base_user()
        self.headers['Authorization'] = self.base_authorization()

    def tearDown(self):
        self._context.pop()

    def base_user(self):
        tenant_user = User.query.filter_by(email='emq@emqtt.com').first()
        if not tenant_user:
            payload = {
                'company': 'EMQ',
                'email': 'emq@emqtt.com',
                'companySize': '100',
                'tenantType': 2,
                'password': hashlib.sha256('public').hexdigest(),
                'mobile': '1234567890',
                'username': 'EMQ'
            }
            response = requests.request('POST', self.api_url + '/signup', json=payload)
            assert response.status_code == 201
            self.tenant_uid = response.json().get('tenantID')
            self.user_id = response.json().get('userIntID')
        else:
            self.tenant_uid = tenant_user.tenantID
            self.user_id = tenant_user.id

    def base_authorization(self):
        payload = {
            'password': hashlib.sha256('public').hexdigest(),
            'email': 'emq@emqtt.com'
        }
        response = requests.request('POST', self.api_url + '/login', json=payload)
        assert response.status_code == 201
        token = response.json().get('token')
        authorization = f'Bearer {token}'
        return authorization


class EmqxRandom(object):
    def __init__(self):
        pass

    @staticmethod
    def random_cn(prefix=None):
        time_now = datetime.now()
        str_time = time_now.strftime('%m%d%H%M%S%f')
        if not prefix:
            prefix = u'单元测试_'
        return ''.join([prefix, str_time, str(randint(1, 100))])

    @staticmethod
    def random_en(prefix=None):
        time_now = datetime.now()
        str_time = time_now.strftime('%m%d%H%M%S%f')
        if not prefix:
            prefix = u'unitTest_'
        return ''.join([prefix, str_time, str(randint(1, 100))])

    @staticmethod
    def random_int_num(num_len=None):
        if not num_len:
            num_len = 6
        return randint(10 ** (num_len - 1), 10 ** num_len)

    @staticmethod
    def random_float_num(between=None):
        if not between:
            between = [1, 2]
        return uniform(between[0], between[1])

    @staticmethod
    def random_str(str_len=None):
        if not str_len:
            str_len = 6
        generated_str = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for _ in range(str_len)
        ])
        return generated_str

    @staticmethod
    def random_time(**kwargs):
        min_year = kwargs.get('year', 2018)
        min_month = kwargs.get('month', 1)
        min_day = kwargs.get('day', 1)
        min_hour = kwargs.get('hour', 1)
        max_year = datetime.now().year
        years = max_year - min_year + 1

        start = datetime(min_year, min_month, min_day, min_hour, 00, 00)
        end = start + timedelta(days=365 * years)
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(int_delta)
        return start + timedelta(seconds=random_second)

    @staticmethod
    def random_email(suffix=None):
        if not suffix:
            suffix = 'emqtt.com'
        random_prefix = ''.join(
            [choice(ascii_letters + digits) for _ in range(3)])
        return '{email}@{suffix}'.format(email=random_prefix, suffix=suffix)

    @staticmethod
    def random_str_uuid():
        uid = str(uuid.uuid1()).replace('-', '')
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, uid)).replace('-', '')

    @staticmethod
    def random_num_uuid(num_len):
        time_now = datetime.now()
        random_str = time_now.strftime('%Y%m%d%H%M%S%f')
        str_pre = randint(100000, 1000000)
        str_suf = randint(100000, 1000000)
        random_uuid = ''.join([str(str_pre), random_str, str(str_suf)])
        if num_len:
            random_uuid = random_uuid[:num_len]
        return random_uuid

    @staticmethod
    def random_gps(**kwargs):
        base_log = kwargs.get('base_log', 113.16)
        base_lat = kwargs.get('base_lat', 27.83)
        radius = kwargs.get('radius', 1000000)
        radius_in_degrees = radius / 111300
        u = float(random.uniform(0.0, 1.0))
        v = float(random.uniform(0.0, 1.0))
        w = radius_in_degrees * math.sqrt(u)
        t = 2 * math.pi * v
        x = w * math.cos(t)
        y = w * math.sin(t)
        longitude = y + base_log
        latitude = x + base_lat
        gps = [longitude, latitude]
        return gps
