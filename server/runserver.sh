#!/usr/bin/env bash

FLASK_DEBUG=True
export FLASK_ENV=development
flask run -h 0.0.0.0 -p 7000
