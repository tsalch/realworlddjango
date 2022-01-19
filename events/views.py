from django.contrib import messages
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from events.forms import EventEnrollForm, EventCreateUpdateForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from events.models import *
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, HttpResponseRedirect


# Create your views here.
@require_POST
def create_review(request):
    response = {
        'ok': False,  # True если отзыв создан успешно, False в противном случае,
        'msg': '',  # Сообщение об ошибке
        'rate': '',  # Оценка отзыва
        'text': '',  # Текст отзыва
        'created': '',  # Дата создания отзыва в формате DD.MM.YYYY
        'user_name': '',  # Полное имя пользователя
    }

    msg = ('Вы уже оставляли отзыв к этому событию', 'Оценка и текст отзыва - обязательные поля',
           'Отзывы могут оставлять только зарегистрированные пользователи',)

    user = request.user
    if user and user.is_authenticated:
        event_id = request.POST.get('event_id', '')
        rate = request.POST.get('rate', '')
        text = request.POST.get('text', '')
        event = get_object_or_404(Event, pk=event_id)
        if Review.objects.filter(user=user, event=event).exists():
            response['msg'] = msg[0]
        elif rate == '' or text == '':
            response['msg'] = msg[1]
        else:
            review = Review.objects.create(user=user, event=event, rate=rate, text=text)
            response['ok'] = True
            response['rate'] = str(review.rate)
            response['text'] = review.text
            response['created'] = review.created.strftime("%d.%m.%Y")
            response['user_name'] = review.user.get_full_name()
    else:
        response['msg'] = msg[2]
    return JsonResponse(response)


class LoginRequiredMixin:
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Недостаточно прав для добавления нового объекта')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Недостаточно прав.')
        return super().post(request, *args, **kwargs)


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['event_number'] = self.object_list.count()
        context['is_auth'] = self.request.user.is_authenticated
        context['category_objects'] = Category.objects.all()
        context['feature_objects'] = Feature.objects.all()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-pk')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        default_object = super().get_object(queryset)
        return default_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_auth'] = self.request.user.is_authenticated
        context['enroll_form'] = EventEnrollForm(initial={'user': self.request.user, 'event': self.object})
        return context

    def get_template_names(self):
        default_template_names = super().get_template_names()
        return default_template_names


class EventCreateView(CreateView):
    model = Event
    template_name = 'events/event_update.html'
    form_class = EventCreateUpdateForm
    success_url = reverse_lazy('events:event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_auth'] = self.request.user.is_authenticated
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Новое событие успешно создано.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventCreateUpdateForm
    template_name = 'events/event_update.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_auth'] = self.request.user.is_authenticated
        enrolls = self.object.enrolls.all()
        reviews = self.object.reviews.all()
        context['reviews'] = reviews
        partps = []
        for enr in enrolls:
            rev = reviews.filter(user=enr.user).first()
            rate = rev.rate if rev else 0
            partps.append({'name': enr.user.get_full_name(), 'email': enr.user.email, 'rate': rate})
        context['partps'] = partps
        return context

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_update.html'
    success_url = reverse_lazy('events:event_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Событие {self.object} удалено.')
        return result


class EventEnrollView(LoginRequiredMixin, CreateView):
    model = Enroll
    form_class = EventEnrollForm

    def get_success_url(self):
        return self.object.event.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        event = form.cleaned_data.get('event', None)
        if not event:
            event = get_object_or_404(Event, pk=form.data.get('event'))
        redirect_url = event.get_absolute_url() if event else reverse_lazy('events:event_list')
        return HttpResponseRedirect(redirect_url)

    def form_valid(self, form):
        messages.success(self.request, f'Вы записаны на {form.cleaned_data["event"]} ')
        return super().form_valid(form)
