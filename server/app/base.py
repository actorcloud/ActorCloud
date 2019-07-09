from werkzeug.routing import Map
from flask import Flask


__all__ = ['CustomFlask']


class CustomMap(Map):
    def __init__(self):
        self._rule_endpoint_dict = {}
        super().__init__()

    def add(self, rulefactory):
        """Add a new rule or factory to the map and bind it.  Requires that the
        rule is not bound to another map.

        :param rulefactory: a :class:`Rule` or :class:`RuleFactory`
        """
        for rule in rulefactory.get_rules(self):
            rule_key = f"{rule.rule}:{rule.methods}"
            if self._rule_endpoint_dict.get(rule_key):
                rule_replace = False
                if rule.endpoint.split('.')[-1].startswith('_private'):
                    rule_replace = True
                elif rule.endpoint.startswith('_private'):
                    rule_replace = True
                if rule_replace:
                    rule_by_endpoint = self._rule_endpoint_dict[rule.rule]
                    delete_rules = self._rules_by_endpoint.pop(rule_by_endpoint)
                    for delete_rule in delete_rules:
                        self._rules.remove(delete_rule)
                else:
                    return

            rule.bind(self)
            self._rules.append(rule)
            self._rule_endpoint_dict[rule_key] = rule.endpoint
            self._rules_by_endpoint.setdefault(rule.endpoint, []).append(rule)
        self._remap = True


class CustomFlask(Flask):
    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)
        self.url_map = CustomMap()

    def deploy(self):
        """ Project deploy """
        ...

    def upgrade(self):
        """ Project upgrade """
        ...

    def sensors(self):
        """ Sensors monitor app """
        ...
