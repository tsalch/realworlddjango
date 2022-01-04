from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from events.models import *


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


def event_list(request):
    user = request.user
    context = {
        'is_auth': user and user.is_authenticated,
        'category_objects': Category.objects.all(),
        'feature_objects': Feature.objects.all(),
        'event_objects': Event.objects.all(),
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user = request.user
    context = {
        'is_auth': user and user.is_authenticated,
        'event': event,
    }
    return render(request, 'events/event_detail.html', context)
