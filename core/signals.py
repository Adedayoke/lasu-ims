from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Asset, Requisition, Transaction, MaintenanceLog, AuditLog


def _log(instance, action, user=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
    )


@receiver(post_save, sender=Asset)
def log_asset_save(sender, instance, created, **kwargs):
    verb = 'Created' if created else 'Updated'
    _log(instance, f'{verb} asset {instance.asset_id} — {instance.name}', user=getattr(instance, '_current_user', None))


@receiver(post_delete, sender=Asset)
def log_asset_delete(sender, instance, **kwargs):
    _log(instance, f'Deleted asset {instance.asset_id} — {instance.name}', user=getattr(instance, '_current_user', None))


@receiver(post_save, sender=Requisition)
def log_requisition_save(sender, instance, created, **kwargs):
    verb = 'Created' if created else 'Updated'
    _log(instance, f'{verb} requisition {instance.req_number} (status: {instance.status})', user=getattr(instance, '_current_user', None))


@receiver(post_save, sender=Transaction)
def log_transaction_save(sender, instance, created, **kwargs):
    if created:
        _log(instance, f'Transaction {instance.transaction_id}: {instance.get_transaction_type_display()} asset {instance.asset.asset_id}', user=instance.performed_by)


@receiver(post_save, sender=MaintenanceLog)
def log_maintenance_save(sender, instance, created, **kwargs):
    verb = 'Reported' if created else 'Updated'
    _log(instance, f'{verb} maintenance for {instance.asset.asset_id} — status: {instance.status}', user=getattr(instance, '_current_user', None))
