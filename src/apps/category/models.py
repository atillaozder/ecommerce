from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver
from utils.utils import unique_slug_generator



class Category(models.Model):

    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

@receiver(pre_save, sender=Category)
def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)