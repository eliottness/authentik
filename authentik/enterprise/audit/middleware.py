"""Enterprise audit middleware"""
from copy import deepcopy
from functools import partial
from typing import Callable

from deepdiff import DeepDiff
from django.apps.registry import apps
from django.core.files import File
from django.db import connection
from django.db.models import Model
from django.db.models.expressions import BaseExpression, Combinable
from django.db.models.signals import post_init
from django.http import HttpRequest, HttpResponse

from authentik.core.models import User
from authentik.events.middleware import AuditMiddleware, should_log_model
from authentik.events.utils import cleanse_dict, sanitize_item


class EnterpriseAuditMiddleware(AuditMiddleware):
    """Enterprise audit middleware"""

    _enabled = False

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        super().__init__(get_response)
        self._enabled = apps.get_app_config("authentik_enterprise").enabled()

    def connect(self, request: HttpRequest):
        super().connect(request)
        if not self._enabled:
            return
        user = getattr(request, "user", self.anonymous_user)
        if not user.is_authenticated:
            user = self.anonymous_user
        if not hasattr(request, "request_id"):
            return
        post_init.connect(
            partial(self.post_init_handler, user=user, request=request),
            dispatch_uid=request.request_id,
            weak=False,
        )

    def disconnect(self, request: HttpRequest):
        super().disconnect(request)
        if not self._enabled:
            return
        if not hasattr(request, "request_id"):
            return
        post_init.disconnect(dispatch_uid=request.request_id)

    def serialize_simple(self, model: Model) -> dict:
        """Serialize a model in a very simple way. No ForeginKeys or other relationships are
        resolved"""
        data = {}
        deferred_fields = model.get_deferred_fields()
        for field in model._meta.concrete_fields:
            value = None
            if field.remote_field:
                continue

            if field.get_attname() in deferred_fields:
                continue

            field_value = getattr(model, field.attname)
            if isinstance(value, File):
                field_value = value.name

            # If current field value is an expression, we are not evaluating it
            if isinstance(field_value, (BaseExpression, Combinable)):
                continue
            field_value = field.to_python(field_value)
            data[field.name] = deepcopy(field_value)
        return cleanse_dict(data)

    def diff(self, before: dict, after: dict) -> dict:
        """Generate diff between dicts"""
        return DeepDiff(sanitize_item(before), sanitize_item(after))

    def post_init_handler(self, user: User, request: HttpRequest, sender, instance: Model, **_):
        """post_init django model handler"""
        if not should_log_model(instance):
            return
        if hasattr(instance, "_previous_state"):
            return
        before = len(connection.queries)
        setattr(instance, "_previous_state", self.serialize_simple(instance))
        after = len(connection.queries)
        if after > before:
            raise AssertionError("More queries generated by serialize_simple")

    # pylint: disable=too-many-arguments
    def post_save_handler(
        self,
        user: User,
        request: HttpRequest,
        sender,
        instance: Model,
        created: bool,
        thread_kwargs: dict | None = None,
        **_,
    ):
        if not should_log_model(instance):
            return None
        thread_kwargs = {}
        if hasattr(instance, "_previous_state") or created:
            prev_state = getattr(instance, "_previous_state", {})
            # Get current state
            new_state = self.serialize_simple(instance)
            thread_kwargs["diff"] = self.diff(prev_state, new_state)
        return super().post_save_handler(
            user, request, sender, instance, created, thread_kwargs, **_
        )
