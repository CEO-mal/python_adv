from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

from .models import Task


class StatusNotificationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            "owner", "owner@example.com", "Kv7Rt2Wq9X"
        )
        self.task = Task.objects.create(
            title="Подготовить отчёт",
            deadline=timezone.now() + timedelta(days=3),
            owner=self.owner,
        )
        mail.outbox.clear()

    def change(self, status):
        self.task.status = status
        self.task.save()

    def test_no_email_on_create(self):
        with self.captureOnCommitCallbacks(execute=True):
            Task.objects.create(
                title="Новая", deadline=timezone.now() + timedelta(days=1), owner=self.owner
            )
        self.assertEqual(len(mail.outbox), 0)

    def test_status_change_sends_email_to_owner(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.change("in_progress")
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["owner@example.com"])
        self.assertIn("Подготовить отчёт", message.subject)
        self.assertIn("In progress", message.body)

    def test_closing_task_sends_closed_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.change("done")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("закрыта", mail.outbox[0].subject)

    def test_same_status_does_not_send_again(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.change("in_progress")
        mail.outbox.clear()
        with self.captureOnCommitCallbacks(execute=True):
            self.change("in_progress")  # тот же статус
        self.assertEqual(len(mail.outbox), 0)

    def test_other_field_change_does_not_send_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.task.description = "Новое описание"
            self.task.save()
        self.assertEqual(len(mail.outbox), 0)

    def test_series_of_changes_in_one_transaction_sends_single_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.change("in_progress")
            self.change("done")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("закрыта", mail.outbox[0].subject)
        self.assertIn("New -> Done", mail.outbox[0].body)

    def test_status_returned_to_original_sends_nothing(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.change("in_progress")
            self.change("new")
        self.assertEqual(len(mail.outbox), 0)

    def test_separate_changes_send_separate_emails(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.change("in_progress")
        with self.captureOnCommitCallbacks(execute=True):
            self.change("done")
        self.assertEqual(len(mail.outbox), 2)

    def test_no_email_without_owner(self):
        self.task.owner = None
        self.task.save()
        with self.captureOnCommitCallbacks(execute=True):
            self.change("in_progress")
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_when_owner_has_no_email(self):
        self.owner.email = ""
        self.owner.save()
        with self.captureOnCommitCallbacks(execute=True):
            self.change("in_progress")
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_if_transaction_rolled_back(self):
        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    self.change("done")
                    raise RuntimeError("откат")
            except RuntimeError:
                pass
        self.assertEqual(len(mail.outbox), 0)
