from django.db import models


class DrowsinessLog(models.Model):
    AWAKE = 'Awake'
    DROWSY = 'Drowsy'

    STATUS_CHOICES = [
        (AWAKE, 'Awake'),
        (DROWSY, 'Drowsy'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    ear_value = models.FloatField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.status} at {self.timestamp:%Y-%m-%d %H:%M:%S}'
