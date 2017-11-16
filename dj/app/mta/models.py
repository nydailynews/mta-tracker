from django.db import models
from django.conf import settings

class Mode(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, blank=True, null=True)

    def get_absolute_url(self):
        return self

    class Meta:
        pass

class Line(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    mode = models.ForeignKey(mode)

    def get_absolute_url(self):
        return self

    class Meta:
        pass

class Alert(models.Model):
    cause = models.TextField()
    line = models.ForeignKey(line)
    start = models.DateTimeField()
    stop = models.DateTimeField(blank=True, null=True)

class DelayAlert(Alert):
    pass
