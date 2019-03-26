from . import bp
from app.models import User
from app import auth


@bp.route('/users')
@auth.login_required
def list_users():
    print(User.query.all())
    return ''
