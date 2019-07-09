import logging

from app import create_app


app = create_app()


@app.cli.command('deploy', short_help='Deploy project')
def deploy():
    app.deploy()


@app.cli.command('upgrade', short_help='Upgrade project')
def upgrade():
    app.upgrade()


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
