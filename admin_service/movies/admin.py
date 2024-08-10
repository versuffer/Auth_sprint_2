from django.contrib import admin

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork
from django.utils.translation import gettext_lazy as _


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', )
    search_fields = ('full_name',)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline, )
    list_display = ('title', 'type', 'genre_film_work', 'creation_date', 'rating', 'created', 'modified')
    list_filter = ('type', 'rating', 'creation_date')
    search_fields = ('title', 'description', 'id')
    autocomplete_fields = ('persons', 'genres')

    def genre_film_work(self, obj):
        return [genre for genre in obj.genres.all().prefetch_related('film_works')]

    genre_film_work.short_description = _('genre_film_work')
