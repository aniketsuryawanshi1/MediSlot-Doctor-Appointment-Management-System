from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Mixin to add created_at and updated_at fields to models (GOF: Composition for shared state)."""
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Mixin to add soft delete functionality (GOF: Strategy for deletion behavior)."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark the instance as deleted without removing from DB."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft-deleted instance."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()