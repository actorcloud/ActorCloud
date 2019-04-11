from app import auth
from . import bp


@bp.route('/emq_select/data_points')
@auth.login_required(permission_required=False)
def list_emq_select_data_points():
    ...


@bp.route('/emq_select/data_streams')
@auth.login_required(permission_required=False)
def list_emq_select_data_streams():
    ...
