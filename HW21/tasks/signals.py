import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import STATUS_CHOICES, Task

logger = logging.getLogger(__name__)
STATUS_LABELS = dict(STATUS_CHOICES)


@receiver(pre_save, sender=Task)
def remember_old_status(sender, instance, **kwargs):
    """Перед сохранением запоминаем статус, который сейчас лежит в базе."""
    if instance.pk:
        instance._old_status = (
            Task.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        )
    else:
        instance._old_status = None  # новая задача


@receiver(post_save, sender=Task)
def notify_owner_about_status_change(sender, instance, created, **kwargs):
    """После сохранения: если статус изменился - письмо владельцу задачи."""
    if created:
        return  # при создании задачи уведомление не нужно

    old_status = getattr(instance, "_old_status", None)
    new_status = instance.status
    if old_status is None or old_status == new_status:
        return  # статус не менялся (правили описание, дедлайн и т.д.) - письма нет

    notice = instance.__dict__.get("_status_notice")
    if notice is not None:
        # Серия изменений в одной транзакции: письмо уже запланировано,
        # просто обновляем итоговый статус (письмо будет одно).
        notice["new"] = new_status
        return

    instance._status_notice = {"old": old_status, "new": new_status}
    # Письмо уходит только после успешного сохранения в базу (не при откате).
    transaction.on_commit(lambda: _send_notice(instance))


def _send_notice(task):
    notice = task.__dict__.pop("_status_notice", None)
    if not notice or notice["old"] == notice["new"]:
        return  # статус вернулся к исходному - уведомлять не о чем

    owner = task.owner
    if owner is None or not owner.email:
        return  # некому или некуда отправлять

    old_label = STATUS_LABELS.get(notice["old"], notice["old"])
    new_label = STATUS_LABELS.get(notice["new"], notice["new"])
    if notice["new"] == "done":
        subject = f"Задача «{task.title}» закрыта"
        headline = "Ваша задача закрыта."
    else:
        subject = f"Статус задачи «{task.title}» изменён"
        headline = "Статус вашей задачи изменён."

    message = (
        f"Здравствуйте, {owner.username}!\n\n"
        f"{headline}\n"
        f"Задача: {task.title}\n"
        f"Статус: {old_label} -> {new_label}\n"
        f"Дедлайн: {task.deadline:%d.%m.%Y %H:%M}\n\n"
        "Это автоматическое уведомление менеджера задач."
    )
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [owner.email])
    except Exception:  # ошибка почты не должна ломать работу API
        logger.exception("Не удалось отправить уведомление по задаче %s", task.pk)
