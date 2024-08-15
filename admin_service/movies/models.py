import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        abstract = True


class TimeStampedMixin(CreatedMixin):
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full_name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('person')
        verbose_name_plural = _('persons')

    def __str__(self):
        return self.full_name


class FilmWork(UUIDMixin, TimeStampedMixin):

    class Type(models.TextChoices):
        MOVIE = 'movie', _('movie')
        TV_SHOW = 'tv_show', _('tv_show')

    title = models.CharField(_('title'))
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateTimeField(_('creation_date'), blank=True, null=True)
    rating = models.FloatField(_('rating'), blank=True, null=True, validators=[
        MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(_('type'), choices=Type.choices, default=Type.MOVIE)
    genres = models.ManyToManyField(
        Genre, through='GenreFilmwork', verbose_name=_('genres'), related_name='film_works')
    persons = models.ManyToManyField(
        Person, through='PersonFilmwork', verbose_name=_('persons'), related_name='film_works')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('film_work')
        verbose_name_plural = _('film_works')
        ordering = ('-rating',)

    def __str__(self):
        return self.title


class GenreFilmWork(UUIDMixin, CreatedMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE, verbose_name=_('film_work'))
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, verbose_name=_('genre'))

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('genre_film_work')
        verbose_name_plural = _('genre_film_works')
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'genre'], name='unique_film_work_genre')
        ]

    def __str__(self):
        return (f'{self.genre._meta.verbose_name}: {self.genre.name}, '
                f'{self.film_work._meta.verbose_name}: {self.film_work}')


class PersonFilmWork(UUIDMixin, CreatedMixin):

    class Role(models.TextChoices):
        ACTOR = 'actor', _('actor')
        DIRECTOR = 'director', _('director')
        WRITER = 'writer', _('writer')

    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE, verbose_name=_('film_work'))
    person = models.ForeignKey('Person', on_delete=models.CASCADE, verbose_name=_('person'))
    role = models.CharField(max_length=255, verbose_name=_('role'), choices=Role.choices, default=Role.ACTOR)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('person_film_work')
        verbose_name_plural = _('person_film_works')
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='unique_film_work_person_role')
        ]

    def __str__(self):
        return (f'{self.person._meta.verbose_name}: {self.person.full_name}, '
                f'{self.film_work._meta.verbose_name}: {self.film_work.title}')
