from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


class MenstrualCycle(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='menstrual_cycle'
    )

    last_period = models.DateField()
    cycle_length = models.IntegerField(help_text="Cycle length in days")
    period_duration = models.IntegerField(help_text="Duration of period in days")
    cycle_regular = models.BooleanField(help_text="Is the cycle regular?")

    # ✅ New health fields
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  # in cm
    weight = models.FloatField(null=True, blank=True)  # in kg

    def __str__(self):
        return f"{self.user.username}'s Menstrual Cycle"

    # ✅ BMI calculator
    def calculate_bmi(self):
        if self.height and self.weight:
            return self.weight / ((self.height / 100) ** 2)
        return None

    def get_days_passed(self):
        today = date.today()
        return (today - self.last_period).days

    def get_progress_percentage(self):
        days_passed = self.get_days_passed()
        return (days_passed / self.cycle_length) * 100 if self.cycle_length else 0

    def get_period_end_date(self):
        return self.last_period + timedelta(days=self.period_duration)

    def is_in_period(self):
        today = date.today()
        period_end_date = self.get_period_end_date()
        return self.last_period <= today <= period_end_date
