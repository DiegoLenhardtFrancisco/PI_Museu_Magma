import uuid
from django.db import models
from core.models import AuditModel


class Visitor(AuditModel, models.Model):
    """
    Represents a museum visitor or visitor group.
    Stores personal data for identification and future visits.
    """

    VISITOR_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Individual'),
        ('GROUP', 'Grupo'),
        ('SCHOOL', 'Grupo Escolar'),
        ('GUIDED', 'Tour Guiado'),
    ]

    name = models.CharField(max_length=150)
    document = models.CharField(max_length=20, blank=True)
    visitor_type = models.CharField(
        max_length=20,
        choices=VISITOR_TYPE_CHOICES,
        default='INDIVIDUAL',
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Visitante'
        verbose_name_plural = 'Visitantes'

    def __str__(self):
        return f"{self.name}"


class Visit(models.Model):
    """
    Represents a single visit to the museum.
    Created on check-in, completed on check-out.
    The ticket_code UUID is used to generate the QR Code.
    """

    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE,
        related_name='visits',
    )
    ticket_code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )
    check_in_at = models.DateTimeField(auto_now_add=True)
    check_out_at = models.DateTimeField(null=True, blank=True)
    companion_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    registered_by = models.ForeignKey(
        'usuarios.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_visits',
    )

    class Meta:
        ordering = ['-check_in_at']
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'

    @property
    def is_active(self):
        """Returns True if the visitor has not checked out yet."""
        return self.check_out_at is None

    @property
    def duration_minutes(self):
        """Returns visit duration in minutes, or None if still active."""
        if self.check_out_at:
            delta = self.check_out_at - self.check_in_at
            return int(delta.total_seconds() / 60)
        return None

    def __str__(self):
        return f"Visit #{self.ticket_code} - {self.visitor.name}"