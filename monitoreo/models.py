from datetime import timedelta

import arrow
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_q.models import Schedule


def round_arrow(time, dt):
    minutes = dt.seconds // 60
    if minutes != 0:
        return time + timedelta(
            minutes=minutes * (time.minute // minutes + 1) - time.minute,
            seconds=-time.second,
            microseconds=-time.microsecond,
        )
    else:
        return time


class Subscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class WatchList(models.Model):
    name = models.SlugField(unique=True)
    subscribers = models.ManyToManyField(Subscriber)
    devices = models.ManyToManyField(
        'todos_los_nodos.IPDevice',
        limit_choices_to=Q(ip__isnull=False),
        verbose_name='device',
    )
    recurrence = models.DurationField()
    active = models.BooleanField(default=False)
    schedule = models.OneToOneField(
        to=Schedule,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.active:
            # create schedule if not exists
            if self.schedule is None:
                self.schedule = Schedule.objects.create(
                    func='monitoreo.tasks.run_watchlist',
                    args=self.pk,  # watchlist instance
                    schedule_type=Schedule.MINUTES,
                    minutes=(self.recurrence.total_seconds() // 60),
                    repeats=-1,
                    cluster='QCluster',
                    next_run=round_arrow(arrow.now(timezone.get_current_timezone()), self.recurrence)
                        .datetime,
                )
        else:
            # delete schedule if exists
            if self.schedule is not None:
                schedule = self.schedule
                self.schedule = None
                schedule.delete()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # delete schedule if exists
        if self.schedule is not None:
            schedule = self.schedule
            self.schedule = None
            schedule.delete()
        super().delete(*args, **kwargs)

# class Status(models.Model):
#     list = models.ForeignKey(WatchList, on_delete=models.CASCADE)
#     ipDevice = models.ForeignKey(
#         'todos_los_nodos.IPDevice',
#         on_delete=models.CASCADE,
#         related_name='+',
#         limit_choices_to=Q(ip__isnull=False),
#         verbose_name="device",
#     )
#     alive = models.BooleanField(default=False)
#     lastAlive = models.DateTimeField(null=True)
#
#     class Meta:
#         verbose_name_plural = "Status"
