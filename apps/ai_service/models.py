from django.conf import settings
from django.db import models


class AISearchLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_search_logs',
        verbose_name='Foydalanuvchi'
    )
    query_text = models.CharField(max_length=500, verbose_name='So‘rov matni')
    parsed_filters = models.JSONField(default=dict, verbose_name='Ajratib olingan filtrlar')
    recommended_location_ids = models.JSONField(default=list, verbose_name='Tavsiya qilingan IDlar')
    explanation = models.TextField(blank=True, verbose_name='AI tushuntirishi')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AI qidiruv jurnali'
        verbose_name_plural = 'AI qidiruv jurnallari'
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Query: '{self.query_text[:30]}...' ({self.created_at.strftime('%d.%m %H:%M')})"
