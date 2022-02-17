from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth import authenticate, login

from allauth.account.views import LoginView, SignupView

from accounts.forms import (CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm,
                            CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm)
from accounts.models import Profile
from events.models import Event, Enroll, Review
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from utils.transform_data import *


class NullUser:
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('main:index'))
        return super().get(request, *args, **kwargs)


class CustomSignUpView(NullUser, CreateView):
    model = User
    template_name = 'accounts/registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('events:event_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return result


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/registration/signin.html'


class CustomPasswordResetView(LoginRequiredMixin, auth_views.PasswordResetView):
    template_name = 'accounts/registration/password_reset_form.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/registration/password_reset_email.txt'
    subject_template_name = 'accounts/registration/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    html_email_template_name = 'accounts/registration/password_reset_email.html'

    def form_valid(self, form):
        self.request.session['reset_email'] = form.cleaned_data['email']
        return super().form_valid(form)


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/registration/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reset_email'] = self.request.session.get('reset_email', '')
        return context


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/registration/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/registration/password_reset_complete.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    child_model = Profile
    child_form_class = ProfileUpdateForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_child_model(self):
        return self.child_model

    def get_child_fields(self):
        return self.child_fields

    def get_child_form(self, sv=False):
        kwargs = self.get_form_kwargs()
        if hasattr(self, 'object'): kwargs['instance'] = kwargs['instance'].profile
        return self.child_form_class(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'child_form' not in context:
            context['child_form'] = self.get_child_form()
        user = self.request.user
        reviews = user.reviews.select_related('event').all()
        context['reviews'] = reviews
        dict_rev = dict_data(reviews, 'event_id')
        records = user.enrolls.select_related('event').all()
        context['enrolls'] = prepare_data(records, dict_rev, 'event', '--', 'event')
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        child_form = self.get_child_form(True)
        form.instance = self.request.user
        child_form.instance = self.request.user.profile

        # check if both forms are valid
        form_valid = form.is_valid()
        child_form_valid = child_form.is_valid()

        if form_valid and child_form_valid:
            return self.form_valid(form, child_form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, child_form):
        self.object = form.save()
        save_child_form = child_form.save(commit=False)
        save_child_form.course_key = self.object
        save_child_form.save()
        messages.success(self.request, f'Данные успешно обновлены')
        return HttpResponseRedirect(self.get_success_url())
