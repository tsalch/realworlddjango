from django.views.generic import TemplateView

from events.models import Event, Review


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.all().order_by('-pk')[:3]
        context['reviews'] = Review.objects.all().order_by('-pk')[:3]
        context['main'] = True
        division_by_zero = 1 / 0
        return context
