# PI_Museu_Magma/core/models.py (UPDATED)
from django.conf import settings
from django.db import models

class AuditModel(models.Model):
    """
    An abstract base class model that provides self-updating
    `created_at`, `updated_at`, `created_by`, and `updated_by` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        editable=False
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        editable=False
    )

    class Meta:
        abstract = True