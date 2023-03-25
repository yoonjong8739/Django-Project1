from django.db import models


# Create your models here.
class TrendingBooks(models.Model):
    weekly_rank = models.IntegerField()
    isbn_n = models.CharField(max_length=100)
    isbn_m = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    writer = models.CharField(max_length=100)
    image = models.TextField()
    rank_total = models.FloatField()
    commentary_total = models.FloatField()
    rank_total_nz = models.FloatField()
    commentary_total_nz = models.FloatField()
    final_score_nz = models.FloatField()
    date = models.DateTimeField()

    def __str__(self):
        info = f"{self.weekly_rank}위 제목: {self.title}, 작가: {self.writer}"
        return info


