from django.db import models

class CorpusFile(models.Model):
    uploaded_file_name = models.CharField(max_length=255)
    stored_file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(max_length=64, unique=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return self.uploaded_file_name

class Posting(models.Model):
    term = models.CharField(max_length=255)
    positions = models.JSONField()

    def __str__(self):
        return self.term
