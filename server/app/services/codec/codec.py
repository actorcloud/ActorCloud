import json
import os
import random
import re
import string
from importlib import import_module
from inspect import signature

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException


app = Flask(__name__)


@app.route('/api/v1/codec', methods=['POST'])
def code_run():
    """
    codec python script description:
    - decode(topic, message):
    Args:
        topic (bytes): The topic of this message.
        message (bytes): The payload of the message.
    Returns:
      Tuple: (status_code, result)
             `status_code`: integer, 0 - OK, 1 - ERROR.
             `result`: bytes, a JSON string bytes that complies with the data structures
                       defined in the schema file.
    - encode(topic, message):
    Args:
        topic (bytes): The topic of this message.
        message (bytes): The payload of the message, this message is of the format
                     defined in the schema file.
    Returns:
      Tuple: (status_code, result)
             `status_code`: integer, 0 - OK, 1 - ERROR.
             `result`: bytes, a message in the format the client requires.
    """
    request_json = request.get_json()
    code = request_json.get('code')
    name = get_name()
    input_msg = request_json.get('input')
    topic = request_json.get('topic')
    analog_type = request_json.get('analogType')
    field_name = 'decode' if analog_type == 1 else 'encode'
    fpath = write_py(name, code)
    response = {}
    try:
        codec_module = import_module(f'_temp.{name}')

        white_list = ['datetime', 'time', 'json', 'sys', 'struct', 'base64']

        for i in ['decode', 'encode']:
            if i not in dir(codec_module):
                raise Exception(f'{i} function required')

        # validate import
        # ['import json\n', 'from datetime import datetime\n']
        import_expressions = re.findall(r'.*import.*\n*', code)
        for i in import_expressions:
            # get content after import,there are three situations generally:
            # json;pandas as pd;sys,os
            m = re.sub(r'.*import\s', '', i).replace('\n', '').strip()
            modules = re.split(r'[,\s]+', m)
            if 'as' in modules:
                modules = modules[:1]
            for module in modules:
                if module not in white_list:
                    raise Exception(f'Invalid import: {module}')

        if analog_type == 1:
            run_func = codec_module.decode
        else:
            run_func = codec_module.encode
        # validate parameters
        if len(signature(run_func).parameters) != 2:
            raise Exception('Required 2 arguments')
        input_msg = input_msg.encode().decode('unicode_escape')
        bytes_message = bytes(map(ord, input_msg))
        status_code, result = run_func(topic.encode(), bytes_message)
        # validate status code
        if status_code not in [0, 1]:
            raise Exception('status code must be 0 or 1')
        # validate result type and format
        if not isinstance(result, bytes):
            raise Exception('result must a JSON string bytes')
        if analog_type == 1:
            try:
                result = json.loads(result)
            except Exception:
                if status_code == 0:
                    raise Exception('result must a JSON string bytes')
                else:
                    result = result.decode()
        else:
            # Encode，return encode result with str
            result = str(result)

        response['output'] = {
            'status_code': status_code,
            'result': result
        }
    except Exception as e:
        response['error'] = {field_name: str(e)}
    finally:
        os.remove(fpath)

    return jsonify(response)


def write_py(name, code):
    temp_dir = os.getcwd() + '/_temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        with open(temp_dir + '/__init__.py', 'w') as f:
            f.write('')
    fpath = os.path.join(temp_dir, '%s.py' % name)
    with open(fpath, 'w') as f:
        f.write(code)
    return fpath


def get_name():
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    return f'codec_{random_str}'


if __name__ == '__main__':
    app.run('0.0.0.0', 7002, debug=True)
