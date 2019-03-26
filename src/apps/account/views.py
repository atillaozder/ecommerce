from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    get_user_model,
    update_session_auth_hash,
    authenticate
)

from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    INTERNAL_RESET_SESSION_TOKEN
)

from .forms import UserPasswordChangeForm, UserSetPasswordForm, UserRegisterForm
from django.views.generic import View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()


class UserLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = False

    def form_valid(self, form):
        user = form.get_user()
        if user.is_distributor() and not user.is_approved():
            info_message = _('Your membership must be approved by admin.')
            messages.add_message(self.request, messages.INFO, info_message)
        else:
            auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


class UserRegisterView(CreateView):
    template_name = 'authentication/register.html'
    form_class = UserRegisterForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        context = {'form': self.form_class}
        return render(request, 'authentication/register.html', context)

    def form_valid(self, form):
        valid = super(UserRegisterView, self).form_valid(form)
        if valid:
            user = form.instance
            if user.is_distributor():
                info_message = _('Your request is sent. Please wait for approvement of admin.')
                messages.add_message(self.request, messages.INFO, info_message)
            else:
                username = self.request.POST.get("username").strip()
                password = self.request.POST.get("password")
                user = authenticate(username=username, password=password)
                auth_login(self.request, user)
        return valid

    def get_success_url(self):
        return reverse_lazy('home')


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


class UserDetailView(View):

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username', None)
        context = {}
        if username:
            user = get_object_or_404(User, username=username)
            context['object'] = user
        return render(request, "user_profile.html", context)


class UserDeleteView(LoginRequiredMixin, View):

    def post(self):
        user = self.request.user
        user.is_active = False
        auth_logout(user)
        user.save()
        return redirect('users:login')


class UserUpdateView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "user_update.html", {})

    def post(self, request):
        user = self.request.user
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return redirect(user.get_absolute_url())


class UserImageUpdateView(LoginRequiredMixin, View):

    def post(self, request):
        user = self.request.user
        image = request.FILES.get("profile_image", None)
        if image:
            user.image = image
            user.save()
        return redirect(user.get_absolute_url())