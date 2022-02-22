from threading import Thread

from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from mail.models import Subscriber, Letter


@require_POST
def create_letters_view(request):
    emails = request.POST.getlist('email', None)
    subject = request.POST.get('subject', '')
    text = request.POST.get('text', '')
    if emails and subject and text:
        Letter.create_letters(emails, subject, text)

    return JsonResponse({'subscribers': Subscriber.get_objects_list()})


class SendTread(Thread):
    def __init__(self, letter, tn):
        super().__init__()
        self.letter = letter
        self.tn = tn

    def run(self):
        if send_mail(self.letter.subject, self.letter.text, None, [self.letter.to],
                     fail_silently=False, ) == 1:
            self.letter.is_sent = True
            self.letter.save()
            self.sent = True
            print(f'Поток {self.tn} - успех')
        else:
            self.sent = False
            print(f'Поток {self.tn} - сбой')


def send_letters(request):
    th_count = 10
    qls = Letter.objects.filter(is_sent=False)
    threads_list = []
    tn = 0
    sent = 0
    for letter in qls:
        if tn < th_count:
            th = SendTread(letter, tn)
            th.start()
            threads_list.append(th)
            tn += 1
        else:
            sent += del_th(threads_list)
            tn = 0
    sent += del_th(threads_list)
    return JsonResponse({'sent': sent})


def del_th(threads_list):
    sent = 0
    while threads_list:
        for thread in threads_list:
            if not thread.is_alive():
                sent += 1 if thread.sent else 0
                threads_list.remove(thread)
    return sent


def get_subscribers(request):
    notall = Letter.objects.filter(is_sent=False).exists()
    return JsonResponse({'subscribers': Subscriber.get_objects_list(), 'all_emails_sent': notall})
