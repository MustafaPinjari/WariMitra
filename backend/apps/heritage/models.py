from django.db import models

class Saint(models.Model):
    name = models.CharField(max_length=200)
    marathi_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    era = models.CharField(max_length=100)
    biography = models.TextField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Abhang(models.Model):
    saint = models.ForeignKey(Saint, on_delete=models.CASCADE, related_name='abhangs')
    title = models.CharField(max_length=200)
    marathi_title = models.CharField(max_length=200)
    lyrics = models.TextField()
    translation = models.TextField(blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)

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
