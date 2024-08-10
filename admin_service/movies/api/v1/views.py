from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import FilmWork, PersonFilmWork
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        filmworks = FilmWork.objects.values(
            'id', 'creation_date', 'rating', 'type', 'title', 'description'
        ).annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg(
                'persons__full_name', filter=Q(personfilmwork__role=PersonFilmWork.Role.ACTOR), distinct=True),
            directors=ArrayAgg(
                'persons__full_name', filter=Q(personfilmwork__role=PersonFilmWork.Role.DIRECTOR), istinct=True),
            writers=ArrayAgg(
                'persons__full_name', filter=Q(personfilmwork__role=PersonFilmWork.Role.WRITER), distinct=True)
        )

        return filmworks

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):

    page_size = 100

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, self.page_size)

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        context = queryset.get(id=self.kwargs['pk'])
        return context
