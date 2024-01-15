"""Enterprise app config"""
from django.conf import settings

from authentik.blueprints.apps import ManagedAppConfig


class EnterpriseConfig(ManagedAppConfig):
    """Base app config for all enterprise apps"""


class AuthentikEnterpriseConfig(EnterpriseConfig):
    """Enterprise app config"""

    name = "authentik.enterprise"
    label = "authentik_enterprise"
    verbose_name = "authentik Enterprise"
    default = True

    def reconcile_load_enterprise_signals(self):
        """Load enterprise signals"""
        self.import_module("authentik.enterprise.signals")

    def reconcile_install_middleware(self):
        """Install enterprise audit middleware"""
        orig_import = "authentik.events.middleware.AuditMiddleware"
        new_import = "authentik.enterprise.middleware.EnterpriseAuditMiddleware"
        settings.MIDDLEWARE = [new_import if x == orig_import else x for x in settings.MIDDLEWARE]
