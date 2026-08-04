from django.db import models

class Saint(models.Model):
    name = models.CharField(max_length=200)
    marathi_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True, default='')
    era = models.CharField(max_length=100, blank=True, default='')
    biography = models.TextField(blank=True, default='')
    image_url = models.URLField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.name

class Abhang(models.Model):
    CATEGORY_CHOICES = [
        ('Abhang', 'Abhang (अभंग)'),
        ('Haripath', 'Haripath (हरिपाठ)'),
        ('Pasaydan', 'Pasaydan (पसायदान)'),
        ('Bhajan', 'Bhajan (भजन)'),
        ('Kirtan', 'Kirtan (कीर्तन)'),
        ('Information', 'Information Guide (माहिती)'),
    ]

    saint = models.ForeignKey(Saint, on_delete=models.SET_NULL, null=True, blank=True, related_name='abhangs')
    title = models.CharField(max_length=200)
    marathi_title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200, blank=True, default='')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Abhang')
    lyrics = models.TextField(blank=True, default='')
    translation = models.TextField(blank=True, null=True)
    audio_url = models.URLField(max_length=1000, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, default='03:30')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at', 'id']

    def __str__(self):
        return self.title


class PilgrimageMilestone(models.Model):
    name = models.CharField(max_length=200)
    marathi_name = models.CharField(max_length=200)
    significance = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    day_number = models.IntegerField(default=1)

    def __str__(self):
        return self.name
