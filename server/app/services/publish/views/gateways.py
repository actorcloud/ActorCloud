import json
import re
from collections import defaultdict
from typing import Dict

from flask import jsonify, request, g, current_app

from actor_libs.database.orm import db
from actor_libs.decorators import ip_limit
from actor_libs.errors import (
    FormInvalid, AttributeUndefined, APIException
)
from actor_libs.http_tools import SyncHttp
from actor_libs.http_tools.responses import handle_emqx_publish_response
from actor_libs.tasks.task import get_task_result
from actor_libs.utils import generate_uuid
from app import auth
from app.models import (
    DictCode, Gateway, Device, DataPoint, PublishLog
)
from . import bp


@bp.route('/gateway_publish', methods=['POST'])
@auth.login_required
def gateway_publish():
    request_json = request.get_json()
    gateway_id = request_json.get('gateway')
    if not gateway_id:
        raise FormInvalid(field='gateway')
    gateway, payload = get_gateway_payload(gateway_id)
    record = emqx_gateway_publish(gateway, payload, g.user_id)
    if record.get('status') != 3:
        raise APIException(field='gateway_publish')
    return jsonify(record), 201


@bp.route('/gateways/<int:gateway_id>/publish_logs')
@auth.login_required
def gateway_publish_logs(gateway_id):
    gateway = Gateway.query.with_entities(Gateway.deviceID) \
        .filter(Gateway.id == gateway_id).first_or_404()

    control_query = PublishLog.query \
        .filter(PublishLog.clientIntID == gateway.deviceID)
    records = control_query.pagination(code_list=['publishStatus'])
    return jsonify(records)


@bp.route('/gateway/publish_callback', methods=['POST'])
@ip_limit
def gateway_publish_callback():
    """
    网关回调接口：
    Gateway callback
    1.normal callback
    2.EMQX forward Neuron gateway response
    Neuron gateway：
    success: {'func':4, 'kbid':{task_id}}
    fail: {'errc':1, 'efun':4,'kbid':{task_id}}
    """

    request_data = request.get_data()
    try:
        request_dict = json.loads(re.sub(r'\x00$', '', request_data))
    except ValueError:
        raise APIException()
    # normal callback
    task_uid = request_dict.get('task_id')
    if task_uid:
        publish_log = PublishLog.query. \
            filter(PublishLog.taskID == task_uid).first()
        publish_log.publishStatus = 2
        db.session.commit()

    # Neuron gateway response
    kbid = request_dict.get('kbid')
    if kbid:
        query = PublishLog.query \
            .join(Gateway, Gateway.id == PublishLog.clientIntID) \
            .with_entities(PublishLog, Gateway) \
            .filter(PublishLog.taskID == kbid) \
            .first()
        if query:
            publish_log, gateway = query
            if 'errc' in request_dict:
                publish_log.publishStatus = 5
            else:
                publish_log.publishStatus = 4
                gateway_func = request_dict.get('func')
                if gateway_func == 4:
                    # Config success,then restart to apply config
                    payload = {
                        'func': 40,
                        'acts': 'restartnew',
                        'kbid': generate_uuid()
                    }
                    emqx_gateway_publish(gateway, payload, publish_log.userIntID)
        db.session.commit()
    return '', 201


def emqx_gateway_publish(gateway: Gateway, payload: dict, user_id: int) -> Dict:
    """ Neuron gateway """

    topic = f'{gateway.deviceID}/Request'
    publish_log = PublishLog(
        deviceIntID=gateway.id,
        payload=payload,
        userIntID=user_id,
        taskID=payload.get('kbid'),
        topic=topic,
        publishStatus=1,
        controlType=1
    )
    db.session.add(publish_log)
    db.session.flush()
    task_uid = publish_log.taskID

    callback = current_app.config.get('GATEWAY_CALLBACK_URL')
    request_payload = {
        'topic': topic,
        'protocol': 'mqtt',
        'tenantID': gateway.tenantID,
        'productID': gateway.productID,
        'deviceID': gateway.deviceID,
        'qos': 1,
        'callback': callback,
        'payload': json.dumps(payload),
        'task_id': task_uid
    }
    request_url = current_app.config.get('MQTT_PUBLISH_URL')
    emqx_auth = current_app.config.get('EMQX_AUTH')

    with SyncHttp(auth=emqx_auth) as sync_http:
        response = sync_http.post(request_url, json=request_payload)
    handled_response = handle_emqx_publish_response(response)
    if handled_response.get('status') == 3:
        task_result = get_task_result(status=3, message='Gateway publish success')
    else:
        publish_log.publishStatus = 0
        task_result = get_task_result(status=4, message=handled_response.get('error'))
    db.session.commit()
    return task_result


def get_gateway_payload(gateway_id):
    """
    Neuron gateway
    Temporarily only supports COM channels
    """
    gateway = Gateway.query \
        .filter(Gateway.id == gateway_id, Gateway.tenantID == g.tenant_uid) \
        .first_or_404()
    channels = gateway.channels
    # validate channel
    if len(channels) != 1:
        raise AttributeUndefined(field='channel')
    channel = channels[0]
    if channel.channelType != 'COM':
        raise AttributeUndefined(field='channel')
    device_int_ids = [result.id for result in gateway.devices]
    # validate child devices
    if not device_int_ids:
        raise AttributeUndefined(field='GroupDevice')
    query_results = Device.query \
        .outerjoin(DataPoint, DataPoint.productID == Device.productID) \
        .filter(Device.id.in_(device_int_ids)) \
        .with_entities(Device.id.label('deviceIntID'),
                       DataPoint.id.label('dataPointIntID'),
                       Device.deviceID, Device.modBusIndex,
                       DataPoint.dataPointID, DataPoint.binarySize,
                       DataPoint.pointDataType, DataPoint.registerAddr,
                       DataPoint.dataTransType, DataPoint.decimal) \
        .all()

    dict_code_list = DictCode.query \
        .filter(DictCode.code == 'pointDataType') \
        .all()
    point_data_type = {
        dict_code.codeValue: dict_code.codeStringValue
        for dict_code in dict_code_list
        if dict_code.codeStringValue is not None
    }
    channel_list = []
    default_channel = {
        "chntype": "dmy",
        "chnix": 0,
        "chnno": 0,
        "chnname": "Dummy",
        "chndrv": "-",
        "tcphost": "",
        "tcpport": 0,
        "ttycom": "",
        "ttybaud": 0,
        "ttydata": 0,
        "ttystop": "",
        "ttypari": "N",
        "ttycts": 0,
        "ttyrts": 0,
        "ttyorts": 0,
        "ttymodm": 0,
        "device": [{
            "tagname": "DUMMY",
            "tagtype": "L",
            "tagarrsz": 100,
            "tagaddr": "-",
            "tagattr": "-",
            "tagupdtime": 0,
            "taglogtime": 0,
            "tagsubno": 0,
            "tagstatus": "NNN"
        }]
    }
    channel_list.append(default_channel)
    channel_dict = {
        # COM channel，fixed value
        "chntype": "tty",
        "chnix": 1,
        "chnno": 1,
        # COM channel，fixed value
        "chnname": "Modbus RTU",
        "chndrv": "simdrv",
        "tcphost": "",
        "tcpport": 0,
        "ttycom": channel.COM,
        "ttybaud": channel.Baud,
        "ttydata": channel.Data,
        "ttystop": channel.Stop,
        "ttypari": channel.Parity,
        "ttycts": 0,
        "ttyrts": 0,
        "ttyorts": 0,
        "ttymodm": 0,
        "device": []
    }
    devices = []
    # data_points
    device_data_point_dict = defaultdict(list)
    for result in query_results:
        if result.dataPointIntID is None:
            raise AttributeUndefined(field='data_point')
        tag_attr = 'R0' if result.dataTransType == 1 else 'W'
        device_dict = {
            "tagaddr": f"{result.modBusIndex}!{result.registerAddr}",
            "tagtype": "L",
            "tagarrsz": result.binarySize,
            "tagname": f"A{result.deviceIntID}{result.dataPointIntID}",
            "tagattr": tag_attr,
            "tagupdtime": 0,
            "taglogtime": 0,
            "tagsubno": 0,
            "tagstatus": "NNN"
        }
        devices.append(device_dict)

        device_data_point_dict[result.deviceIntID].append(result)

    channel_dict['device'] = devices
    channel_list.append(channel_dict)

    object_list = []
    for key in device_data_point_dict.keys():
        device_uid = device_data_point_dict.get(key)[0].deviceID
        object_dict = {
            "objid": "*",
            "objname": device_uid,
            "objdesc": "",
            "objsize": 1,
            "objupdtime": 5,
            "objlogtime": 0,
            "objstatus": "NYYN",
            "objattr": []
        }
        for data_point in device_data_point_dict.get(key):
            attr_dict = {
                "objix": 0,
                "attid": "*",
                "attname": data_point.dataPointID,
                "objprefix": "*",
                "objsuffix": "*",
                "attdesc": "",
                "atttype": point_data_type.get(data_point.pointDataType),
                "decimal": data_point.decimal if data_point.decimal is not None else 0,
                "maxval": 0,
                "minval": 0,
                "preset": 0,
                "unit": "",
                "tagname": f"A{key}{data_point.dataPointID}",
                "tagix": 0,
                "notag": 1,
                "attsubno": 0,
                "attstatus": "NYYN"
            }
            object_dict['objattr'].append(attr_dict)
        object_list.append(object_dict)

    payload = {
        'func': 4,
        'kbid': generate_uuid(),
        'channel': channel_list,
        'object': object_list,
        'message': []
    }
    return gateway, payload
