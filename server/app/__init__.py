from flask import Flask, request
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from flask_uploads import UploadSet, IMAGES, configure_uploads
from sqlalchemy import exc, event
from sqlalchemy.pool import Pool

from actor_libs.auth import HttpAuth
from actor_libs.manage import ProjectManage
from actor_libs.database.orm import db
from config.flask_config import get_flask_config

mail = Mail()
auth = HttpAuth()
migrate = Migrate()
project_manage = ProjectManage()
cros = CORS(resources={r"/api/*": {"origins": "*"}})
images = UploadSet('images', IMAGES + ('ico',))
excels = UploadSet('excels', extensions=('xls', 'xlsx'))
packages = UploadSet('PACKAGES', extensions=('zip', 'tar', 'tgz', '7z'))

app = Flask(__name__, instance_relative_config=True, static_folder='../static')


def create_app():
    # load config
    app.config.update(get_flask_config())

    # init app
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    cros.init_app(app)
    mail.init_app(app)
    configure_uploads(app, (images, excels, packages))

    register_blueprints()
    register_not_found()

    # register extend private app
    try:
        from .private_services import extend_private_app

        extend_private_app(app)
    except ImportError:
        pass
    return app


def register_blueprints():
    from importlib import import_module
    from actor_libs.utils import get_services_path

    active_services = get_services_path()
    for key, value in active_services.items():
        service_path = '.'.join(value.partition('app')[-1].split('/'))
        service_views_path = f'app{service_path}.views'
        views_module = import_module(service_views_path)
        if hasattr(views_module, 'bp'):
            app.register_blueprint(views_module.bp, url_prefix='/api/v1')


def register_not_found():
    from actor_libs.errors import DataNotFound

    @app.errorhandler(404)
    def handle_not_found(error):
        if request.path.startswith('/api/'):
            return DataNotFound('url')
        return error


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connectidon_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except Exception:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()
