from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):

    name = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__ (self):
        return self.name