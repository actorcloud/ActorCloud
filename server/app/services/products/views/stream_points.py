from flask import jsonify

from actor_libs.utils import get_delete_ids
from app import auth
from app.models import StreamPoint, DataStream, DataPoint
from app.schemas import DataPointSchema, StreamPointsSchema
from . import bp


@bp.route('/data_streams/<int:stream_id>/data_points')
@auth.login_required
def view_stream_points(stream_id):
    code_list = ['dataTransType', 'pointDataType']
    data_points = DataPoint.query \
        .join(StreamPoint, StreamPoint.c.dataPointIntID == DataPoint.id) \
        .filter(StreamPoint.c.dataStreamIntID == stream_id).many()
    records = []
    for data_point in data_points:
        records.append(data_point.to_dict(code_list=code_list))
    return jsonify(records)


@bp.route('/data_streams/<int:stream_id>/data_points', methods=['POST'])
@auth.login_required
def create_stream_points(stream_id):
    data_stream = DataStream.query \
        .filter(DataStream.id == stream_id).first_or_404()
    request_dict = DataPointSchema.validate_request()
    data_point = DataPoint()
    created_point = data_point.create(request_dict, commit=False)
    data_stream.dataPoints.append(created_point)
    data_stream.update()
    record = data_point.to_dict()
    return jsonify(record), 201


@bp.route('/data_streams/<int:stream_id>/data_points', methods=['PUT'])
@auth.login_required
def update_stream_points(stream_id):
    data_stream = DataStream.query \
        .filter(DataStream.id == stream_id).first_or_404()
    request_dict = StreamPointsSchema.validate_request()
    data_points = request_dict['dataPoints']
    data_stream.dataPoints = data_points
    data_stream.update()
    record = {
        'dataPoints': [data_point.id for data_point in data_points]
    }
    return jsonify(record)


@bp.route('/data_streams/<int:stream_id>/data_points', methods=['DELETE'])
@auth.login_required
def delete_stream_points(stream_id):
    data_stream = DataStream.query \
        .filter(DataStream.id == stream_id).first_or_404()
    delete_ids = get_delete_ids()
    delete_data_points = DataPoint.query \
        .join(StreamPoint, StreamPoint.c.dataPointIntID == DataPoint.id) \
        .filter(DataPoint.id.in_(delete_ids),
                StreamPoint.c.dataStreamIntID == stream_id) \
        .many(allow_none=False, expect_result=len(delete_ids))
    for delete_data_point in delete_data_points:
        data_stream.dataPoints.remove(delete_data_point)
    data_stream.update()
    return '', 204
