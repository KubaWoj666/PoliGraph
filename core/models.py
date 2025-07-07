from django.db import models

class Video(models.Model):  
    url = models.URLField(max_length=500)

    def __str__(self):
        return self.url


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class TranscriptSegment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="segments")
    start_time = models.FloatField(help_text="Sekundy od początku nagrania")
    end_time = models.FloatField(help_text="Sekundy od początku nagrania")
    text = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="segments", blank=True, null=True)

    def __str__(self):
        return f"{self.video} [{self.start_time}s - {self.end_time}s]"
