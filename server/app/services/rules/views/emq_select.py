from flask import jsonify

from app import auth
from app.models import Action
from . import bp


@bp.route('/emq_select/actions')
@auth.login_required(permission_required=False)
def list_emq_select_actions():
    records = Action.query \
        .with_entities(Action.id.label('value'), Action.actionName.label('label')) \
        .select_options()

    return jsonify(records)
