from django.urls import reverse
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

FILLED_MIDDLE = 50


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=90, default='', verbose_name='Категория')

    def __str__(self):
        return self.title

    def display_event_count(self):
        return self.events.count()

    display_event_count.short_description = 'Количество событий'

    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'


class Feature(models.Model):
    title = models.CharField(max_length=200, default='', verbose_name='Название')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Особенности'
        verbose_name = 'Особенность'


class Event(models.Model):
    title = models.CharField(max_length=200, default='', verbose_name='Название')
    description = models.TextField(default='', verbose_name='Описание')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    participants_number = models.PositiveSmallIntegerField(verbose_name='Количество участников')
    is_private = models.BooleanField(default=False, verbose_name='Частное')
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE, related_name='events',
                                 verbose_name=Category._meta.verbose_name)
    features = models.ManyToManyField(Feature, related_name='events', verbose_name=Feature._meta.verbose_name)
    logo = models.ImageField(upload_to='events/events/', blank=True, null=True)

    condition_list = [
        ('0', lambda x: x <= FILLED_MIDDLE / 100, f'<= {FILLED_MIDDLE}%'),
        ('1', lambda x: FILLED_MIDDLE / 100 < x < 1, f'> {FILLED_MIDDLE}%'),
        ('2', lambda x: x == 1, 'sold-out')
    ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[str(self.pk)])

    def display_enroll_count(self):
        return self.enrolls.count()

    display_enroll_count.short_description = 'Записано'

    def display_places_left(self):
        participants_number = self.participants_number
        enroll_count = self.display_enroll_count()
        rest = participants_number - enroll_count
        ocu_part = enroll_count / participants_number
        for cond in self.condition_list:
            if cond[1](ocu_part): return f'{rest} ({cond[2]})'

    display_places_left.short_description = 'Осталось мест'

    @property
    def rate(self):
        avg_rate = self.reviews.aggregate(models.Avg('rate'))['rate__avg']
        return round(avg_rate, 1)

    @property
    def logo_url(self):
        return self.logo.url if self.logo else f'{settings.STATIC_URL}images/svg-icon/event.svg'

    class Meta:
        verbose_name_plural = 'События'
        verbose_name = 'Событие'


class Enroll(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='enrolls')
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='enrolls',
                              verbose_name=Event._meta.verbose_name)
    created = models.DateTimeField(null=True, auto_now_add=True, verbose_name='Создана')

    def __str__(self):
        return f'{self.user}:{self.created}'

    class Meta:
        verbose_name_plural = 'Записи'
        verbose_name = 'Запись'


class Review(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='reviews',
                             verbose_name=User._meta.verbose_name)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='reviews',
                              verbose_name=Event._meta.verbose_name)
    rate = models.PositiveSmallIntegerField(default=0, verbose_name='Оценка')
    text = models.TextField(verbose_name='Отзыв')
    created = models.DateTimeField(null=True, auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(null=True, auto_now=True, verbose_name='Редакция')

    def __str__(self):
        return f'{self.user} : {self.event} : {self.rate}'

    class Meta:
        verbose_name_plural = 'Отзывы'
        verbose_name = 'Отзыв'
