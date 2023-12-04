"""Import certificate"""
from sys import exit as sys_exit

from django.core.management.base import BaseCommand, no_translations
from django_tenants.management.commands import TenantWrappedCommand
from rest_framework.exceptions import ValidationError
from structlog.stdlib import get_logger

from authentik.crypto.api import CertificateKeyPairSerializer
from authentik.crypto.models import CertificateKeyPair

LOGGER = get_logger()


class TCommand(BaseCommand):
    """Import certificate"""

    @no_translations
    def handle(self, *args, **options):
        """Import certificate"""
        keypair = CertificateKeyPair.objects.filter(name=options["name"]).first()
        dirty = False
        if not keypair:
            keypair = CertificateKeyPair(name=options["name"])
            dirty = True
        with open(options["certificate"], mode="r", encoding="utf-8") as _cert:
            cert_data = _cert.read()
            if keypair.certificate_data != cert_data:
                dirty = True
            keypair.certificate_data = cert_data
        if options["private_key"]:
            with open(options["private_key"], mode="r", encoding="utf-8") as _key:
                key_data = _key.read()
                if keypair.key_data != key_data:
                    dirty = True
                keypair.key_data = key_data
        # Validate that cert and key are actually PEM and valid
        serializer = CertificateKeyPairSerializer(instance=keypair)
        try:
            serializer.validate_certificate_data(keypair.certificate_data)
            if keypair.key_data != "":
                serializer.validate_key_data(keypair.key_data)
        except ValidationError as exc:
            self.stderr.write(str(exc))
            sys_exit(1)
        if dirty:
            keypair.save()

    def add_arguments(self, parser):
        parser.add_argument("--certificate", type=str, required=True)
        parser.add_argument("--private-key", type=str, required=False)
        parser.add_argument("--name", type=str, required=True)


class Command(TenantWrappedCommand):
    COMMAND = TCommand
