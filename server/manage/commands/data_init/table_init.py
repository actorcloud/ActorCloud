import hashlib

from flask import current_app

from actor_libs.database.orm import db
from app.models import (
    SystemInfo, User
)


__all__ = [
    'init_system_info', 'init_admin_account'
]


def init_system_info() -> None:
    """ Initialize system info table """

    system_info_key = (
        'mqttBroker', 'mqttsBroker', 'mqttssBroker', 'coapBroker',
        'coapsBroker', 'coapssBroker', 'wsBroker', 'wssBroker',
        'projectVersion'
    )
    query = db.session.query(SystemInfo.key).all()
    is_exist_keys = [key[0] for key in query]
    for key in system_info_key:
        if key in is_exist_keys:
            continue
        new_system_info = SystemInfo(key=key)
        db.session.add(new_system_info)
    db.session.commit()
    info = "system info table init successfully!"
    print(info)


def init_admin_account() -> None:
    """ Initialize admin user """

    email = current_app.config.get('ADMIN_EMAIL', 'admin@actorcloud.io')
    password = current_app.config.get('ADMIN_PASSWORD', '123456').encode('utf-8')
    admin_user = User(
        username='admin',
        email=email, roleIntID=1,
        password=hashlib.sha256(password).hexdigest()
    )
    db.session.add(admin_user)
    db.session.commit()
    info = "admin user init successfully!"
    print(info)
