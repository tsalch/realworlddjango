from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from realworlddjango.settings import STATIC_URL


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to='accounts/profiles/avatar',
                               verbose_name='Загрузить аватар')

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile', args=[str(self.pk)])

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else f'{STATIC_URL}images/users/profile.svg'
