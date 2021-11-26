from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя в Телеграме',
        unique=True,
    )

    username = models.CharField('Имя пользователя в Телеграме',
                                max_length=50, blank=True, default='')
    first_name = models.CharField('Имя',
                                  max_length=256, blank=True, default='')
    last_name = models.CharField('Фамилия',
                                 max_length=256, blank=True, default='')
    contact = models.CharField('Контакт для связи', max_length=256,
                               blank=True, default='')
    passport = models.CharField('Паспортные данные',
                                 max_length=256, blank=True, default='')
    birthday = models.CharField('Дата рождения',
                                 max_length=256, blank=True, default='')
    
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} ({self.external_id})'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Stuff(models.Model):
    profile = models.ForeignKey(
        to='Profile',
        verbose_name='Профиль',
        on_delete=models.CASCADE,
    )
    storage = models.CharField('Склад', max_length=256, blank=True)
    description = models.CharField('Описание', max_length=256)
    quantity  = models.PositiveIntegerField(verbose_name='Количество')

    period = models.CharField('Период хранения', max_length=256)
    price  = models.PositiveIntegerField(verbose_name='Цена заказа')
    code = models.ImageField(blank=True, upload_to='QR', verbose_name='картинка')

    class Meta:
        verbose_name = 'Вещь'
        verbose_name_plural = 'Вещи'
