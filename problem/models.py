from django.db import models

# Create your models here.
class Problem(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    input_description = models.TextField()
    output_description = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    visible = models.BooleanField(default=False)
    TYPE = (
        ('normal', 'normal judge'),
        ('special', 'special judge'),
        ('error', 'error torrent'),
        ('partial', 'partial judge'),
        ('other', 'other judge'),
    )
    judge_type = models.CharField(max_length=10, choices=TYPE)
    SOURCE = (
        ('uva', 'uva'),
        ('la', 'live archive'),
        ('poj', 'poj'),
        ('zoj', 'zoj'),
    )
    judge_source = models.CharField(max_length=5, choices=SOURCE)
    other_judge_id = models.IntegerField()

    def __str__(self):
        return self.name

