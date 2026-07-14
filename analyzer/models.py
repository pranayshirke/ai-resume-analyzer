from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    resume = models.FileField(upload_to="resumes/")

    ats_score = models.IntegerField(default=0)

    candidate_name = models.CharField(max_length=200, blank=True)

    email = models.EmailField(blank=True)

    phone = models.CharField(max_length=20, blank=True)

    skills = models.TextField(blank=True)
    
    cover_letter = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} ({self.ats_score}%)"