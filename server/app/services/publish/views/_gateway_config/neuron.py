from actor_libs.errors import AttributeUndefined
from app.models import EndDevice, DataPoint


_CHANNEL_DEVICE = {
    "tagname": "DUMMY",
    "tagtype": "L",
    "tagarrsz": 100,
    "tagaddr": "-",
    "tagattr": "-",
    "tagupdtime": 0,
    "taglogtime": 0,
    "tagsubno": 0,
    "tagstatus": "NNN"
}

_CHANNEL = {
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
    "device": [_CHANNEL_DEVICE]
}

_COM_CHANNEL = {
    "chntype": "tty",
    "chnix": 1, "chnno": 1,
    "chnname": "Modbus RTU",
    "chndrv": "simdrv",
    "tcphost": "",
    "tcpport": 0,
    "ttycts": 0,
    "ttyrts": 0,
    "ttyorts": 0,
    "ttymodm": 0,
}

_OBJECT = {
    "objid": "*",
    "objname": '',
    "objdesc": "",
    "objsize": 1,
    "objupdtime": 5,
    "objlogtime": 0,
    "objstatus": "NYYN",
    "objattr": []
}

_OBJECT_ATTR = {
    "objix": 0,
    "attid": "*",
    "attname": '',  # dataPointID
    "objprefix": "*",
    "objsuffix": "*",
    "attdesc": "",
    "atttype": '',  # pointDataType
    "decimal": '',  # decimal
    "maxval": 0,
    "minval": 0,
    "preset": 0,
    "unit": "",
    "tagname": '',  # device id + data_point id
    "tagix": 0,
    "notag": 1,
    "attsubno": 0,
    "attstatus": "NYYN"
}


def neuron_publish_json(request_dict):
    device_id = request_dict['deviceIntID']
    product_uid = request_dict['productID']
    channel = Channel.query\
        .filter(Channel.gateway == device_id,
                Channel.channelType == 'COM').first()
    if not channel:
        raise AttributeUndefined(field='channel')
    gateway_devices = EndDevice.query \
        .filter(EndDevice.gateway == device_id) \
        .with_entities(EndDevice.deviceID, EndDevice.modbusData).all()
    devices_data_point = DataPoint.query \
        .filter(DataPoint.productID == product_uid).all()

    channel_list = [_CHANNEL]
    channel_devices = []
    object_list = []
    for device in gateway_devices:
        device_info = {'deviceID': device.deviceID}
        _CHANNEL_DEVICE.update(device_info)
        channel_devices.append(device_info)
        object_attr_list = []
        for device_data_point in devices_data_point:
            object_attr_info = {
                'attname': device_data_point.dataPointID
            }
            object_attr_list.append(object_attr_info)
        object_attr_info = {
            'objattr': object_attr_list
        }
        _OBJECT.update(object_attr_info)
        object_list.append(_OBJECT)
    _COM_CHANNEL['device'] = channel_devices
    channel_list.append(_COM_CHANNEL)
    publish_json = {
        'func': 4,
        'kbid': request_dict['taskID'],
        'channel': channel_list,
        'object': object_list,
        'message': []
    }
    return publish_json
