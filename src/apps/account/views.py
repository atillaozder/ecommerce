from django.shortcuts import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    get_user_model,
    update_session_auth_hash
)

from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    INTERNAL_RESET_SESSION_TOKEN
)

from apps.account.forms import UserPasswordChangeForm, UserSetPasswordForm

User = get_user_model()


class UserLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = False

    def form_valid(self, form):
        user = form.get_user()
        if user.is_distributor() and not user.is_waiting_approvement():
            info_message = _('Your membership must be approved by admin.')
            messages.add_message(self.request, messages.INFO, info_message)
        else:
            auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'authentication/password_change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        valid = super().form_valid(form)
        if valid:
            info_message = _('Your password has been changed successfully.')
        else:
            info_message = _("We're sorry. An error occurred while trying to "
                             "change your password. Please try again.")

        messages.add_message(self.request, messages.INFO, info_message)
        return valid


class UserPasswordResetView(PasswordResetView):
    template_name = 'authentication/password_reset.html'
    email_template_name = 'authentication/password_reset_email.html'
    subject_template_name = 'authentication/password_reset_subject.html'
    html_email_template_name = 'authentication/password_reset_email.html'
    success_url = reverse_lazy('users:login')
    extra_email_context = {
        'user': '',
        'site': ''
    }

    def form_valid(self, form):
        to_email = form.cleaned_data.get('email')
        qs_exists = User.objects.all().filter(email=to_email).exists()

        if qs_exists:
            user = User.objects.get(email=to_email)
            self.extra_email_context['user'] = user

        current_site = get_current_site(self.request)
        self.extra_email_context['site'] = current_site
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }

        form.save(**opts)
        valid = super().form_valid(form)
        if valid:
            info_message = _("Check your inbox. We've emailed you "
                             "instructions for setting your password. You should "
                             "receive the email shortly!")
        else:
            info_message = _("We're sorry. An error occurred while trying "
                             "to send an email. Please try again.")

        messages.add_message(self.request, messages.INFO, info_message)
        return valid


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = UserSetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    template_name = 'authentication/password_reset_confirm.html'
    success_url = reverse_lazy('users:login')
    title = _('Enter New Password')

    def form_valid(self, form):
        user = form.save()
        if INTERNAL_RESET_SESSION_TOKEN in self.request.session:
            del self.request.session[INTERNAL_RESET_SESSION_TOKEN]

        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)

        valid = super().form_valid(form)
        if valid:
            info_message = _("Your password has been reset successfully. "
                             "You may go ahead and sign in now.")
        else:
            info_message = _("We're sorry. An error occurred while trying "
                             "to reset your password. Please try again.")

        messages.add_message(self.request, messages.INFO, info_message)
        return valid