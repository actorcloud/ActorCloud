import os
from collections import OrderedDict
from typing import AnyStr, Tuple, Dict, List

import yaml
from sqlalchemy import and_

from actor_libs.base_model import db
from actor_libs.utils import get_cwd
from microservices.models import Permission, Resource, Role


__all__ = ['init_default_roles', 'update_default_roles']


def init_default_roles() -> None:
    """
    create default roles and role permissions for project deploy
    """
    roles_info = _get_roles_info()
    roles_resources = _get_roles_resources()

    admin_role = db.session.query(id).first()
    if admin_role:
        raise RuntimeError(u'admin role is exist!')

    for role_name, role_info in roles_info.items():
        role_resources = roles_resources.get(role_name)
        _create_role(role_info, role_resources)

    print('Generate default roles successfully!')


def update_default_roles() -> None:
    """
    update defaut roles
    """
    roles_info = _get_roles_info()
    roles_resources = _get_roles_resources()
    for role_name, role_resource_ids in roles_resources.items():
        role_info = roles_info.get(role_name)
        role = db.session.query \
            .filter(and_(Role.roleName == role_info.get('roleName'),
                         Role.isShare == role_info.get('isShare'),
                         Role.roleType == role_info.get('roleType'))) \
            .first()

        # Create a role if the role does not exist
        if not role:
            _create_role(role_info, role_resource_ids)
        # Update the role if it exists
        else:
            query_resources = db.session.query(Permission.roleIntID,
                                               Permission.resourceIntID) \
                .join(Role, Role.id == Permission.roleIntID) \
                .join(Resource, Resource.id == Permission.resourceIntID) \
                .filter(and_(Role.roleName == role_info.get('roleName'),
                             Role.isShare == role_info.get('isShare'),
                             Role.roleType == role_info.get('roleType'))) \
                .with_entities(Resource.id).all()
            # Insert permissions, if the role does not have any permissions
            if not query_resources:
                for resource_id in role_resource_ids:
                    permission = Permission(
                        roleIntID=role.id, resourceIntID=resource_id
                    )
                    db.session.add(permission)
            # Update permissions
            else:
                query_resources_ids = [resource_id for resource_id in query_resources]
                insert_resource_ids = set(role_resource_ids) \
                    .difference(set(query_resources_ids))
                for insert_resource_id in insert_resource_ids:
                    permission = Permission(
                        roleIntID=role.id, resourceIntID=insert_resource_id
                    )
                    db.session.add(permission)

                delete_resource_ids = set(query_resources_ids) \
                    .difference(set(role_resource_ids))
                for delete_resource_id in delete_resource_ids:
                    permission = Permission.query \
                        .filter_by(roleIntID=role.id, resourceIntID=delete_resource_id) \
                        .first()
                    db.session.delete(permission)
    db.session.commit()
    print('Update default roles successfully!')


def _create_role(role_info: Dict, role_resources: List) -> None:
    """
    insert new role to db
    """
    role = Role()
    new_role = role.create(role_info)
    for resource_id in role_resources:
        role_permission = Permission(
            roleIntID=new_role.id, resourceIntID=resource_id
        )
        db.session.add(role_permission)
    db.session.commit()


def _get_roles_info() -> Dict:
    """
    :return: {'role_name': role_info}
    """
    roles_yml_dict = _load_roles_yml()
    roles = {
        role_name: yml_content.get('role')
        for role_name, yml_content in roles_yml_dict.items()
    }

    # Make sure the super admin user id is 1
    sorted_roles = OrderedDict(
        sorted(roles.items(), key=lambda x: x[1]['order'])
    )

    return sorted_roles


def _get_roles_resources() -> Tuple[Dict, Dict]:
    """
    generate resources for default 9 roles
    :return: {'role_name': [resource_id, ...]}
    """
    roles_resources = {}
    roles_yml_dict = _load_roles_yml()
    for key, yml_content in roles_yml_dict.items():
        query = Resource.query
        resource_method = yml_content.pop('method')
        include_resources = yml_content.pop('include')
        exclude_resources = yml_content.pop('exclude')
        extra_resources = yml_content.pop('extra')

        # 查出各角色对应的resource id
        if resource_method != 'all' and \
           resource_method in ['POST', 'GET', 'DELETE', 'PUT']:
            query = query.filter(Resource.method == resource_method)
        if isinstance(include_resources, list):
            include_ids = []
            for code in include_resources:
                resource_ids = [
                    i[0] for i in _get_resource_children(code)
                ]
                include_ids.extend(resource_ids)
            query = query.filter(Resource.id.in_(include_ids))
        if isinstance(exclude_resources, list):
            exclude_ids = []
            for code in exclude_resources:
                resource_ids = [
                    i[0] for i in _get_resource_children(code)
                ]
                exclude_ids.extend(resource_ids)
            query = query.filter(~Resource.id.in_(exclude_ids))

        role_resource_ids = [resource.id for resource in query.all()]
        if isinstance(extra_resources, list):
            for code in extra_resources:
                resource_ids = [
                    i[0] for i in _get_resource_children(code)
                ]
                role_resource_ids.extend(resource_ids)
        roles_resources[key] = set(role_resource_ids)
    return roles_resources


def _load_roles_yml() -> Dict:
    """
    load default roles yml file
    """
    backend_path = get_cwd()
    default_roles_path = os.path.join(backend_path, 'config/base/default_roles.yml')
    if not os.path.isfile(default_roles_path):
        raise RuntimeError(f"The file {default_roles_path} does not exist.")
    with open(default_roles_path, 'r', encoding='utf-8') as load_file:
        roles_yml = yaml.load(load_file)
        return roles_yml


def _get_resource_children(code: AnyStr) -> List:
    """
    :param code: resource code
    :return: resource id list
    """
    beginning_getter = db.session.query(Resource) \
        .filter(Resource.code == code) \
        .cte(name='children_for', recursive=True)

    with_recursive = beginning_getter.union_all(
        db.session.query(Resource).filter(
            Resource.parentCode == beginning_getter.c.code
        )
    )
    query = db.session.query(with_recursive.c.id) \
        .order_by(beginning_getter.c.createAt) \
        .all()
    return query
