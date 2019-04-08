from flask import g, request
from marshmallow import pre_load, post_load
from marshmallow.validate import OneOf

from actor_libs.errors import DataNotFound
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqDateTime, EmqInteger, EmqList, EmqString
)
from app.models import Product, Application, User


__all__ = ['ApplicationSchema']


class ApplicationSchema(BaseSchema):
    """ application management """

    appID = EmqString(dump_only=True)
    appName = EmqString(required=True)
    appToken = EmqString(dump_only=True)
    expiredAt = EmqDateTime(allow_none=True)  # expired time
    description = EmqString(allow_none=True, len_max=300)
    appStatus = EmqInteger(required=True, validate=OneOf([0, 1]))
    userIntID = EmqInteger(allow_none=True)
    roleIntID = EmqInteger(required=True)  # app role id
    products = EmqList(required=True, list_type=str, load_only=True)  # product uid

    @pre_load
    def update_app_status(self, in_data):
        """ Update application status only on the list """

        app_id = in_data.get('id')
        app_products = in_data.get('products')
        if request.method == 'PUT' and not app_products and app_id:
            app = Application.query \
                .filter(Application.id == app_id).first_or_404()
            in_data['products'] = [product.productID for product in app.products]
        return in_data

    @post_load
    def handle_app_products(self, in_data):
        products_uid = in_data.get('products')
        products = Product.query \
            .join(User, User.id == Product.userIntID) \
            .filter(User.tenantID == g.tenant_uid,
                    Product.productID.in_(set(products_uid))).all()
        if len(products_uid) != len(products):
            raise DataNotFound(field='products')
        in_data['products'] = products
        return in_data
