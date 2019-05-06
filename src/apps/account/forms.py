from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .utils import password_validators_help_text_html
from .models import Distributor
from cart.models import Cart

User = get_user_model()


class AdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Your password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = {
            'email',
        }

    def clean_password2(self):
        # Checks the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Şifreler eşleşmiyor")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(AdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminUpdateForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label='Password',
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password/\">this form</a>."
        ),
    )

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserRegisterForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'username_exists': _("Username is already exists."),
        'email_exists': _("Email is already exists."),
        'password_character': _("Password should be in a character range 6 and 30."),
        'username_character': _("Username should be in a character range 4 and 30."),
        'smaller_than_zero': _("Average salary cannot be smaller than zero"),
    }

    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput, strip=False)
    confirm_password = forms.CharField(label=_('Password again'), widget=forms.PasswordInput, strip=False)

    field_order = [
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'confirm_password',
        'type'
    ]

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autocomplete': 'off'})
        for _, f in self.fields.items():
            f.widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = {
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'type'
        }

        widgets = {
            'password': forms.PasswordInput
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4 or len(username) > 30:
            raise forms.ValidationError(self.error_messages['username_character'])

        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError(self.error_messages['username_exists'])

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError(self.error_messages['email_exists'])
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if not password or not confirm_password:
            raise forms.ValidationError(self.error_messages['password_mismatch'])

        if password != confirm_password:
            raise forms.ValidationError(self.error_messages['password_mismatch'])

        if len(password) < 6 or len(password) > 30:
            raise forms.ValidationError(self.error_messages['password_character'])

        return password

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        password = self.cleaned_data.get('password')
        user.set_password(password)

        if commit:
            user.save()
            user_cart = Cart.objects.create(user=user)
            user_cart.save()
            if user.is_distributor():
                d = Distributor.objects.create(user=user)
                d.save()

        return user


class UserUpdateForm(forms.ModelForm):
    field_order = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['first_name'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('First Name')
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Last name')
        })

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validators_help_text_html(),
    )


class UserPasswordChangeForm(UserSetPasswordForm):
    """
    A form that lets a user change their password by entering their old password.
    """
    error_messages = {
        **SetPasswordForm.error_messages,
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
        'password_mismatch': _("The two password fields didn't match."),
        'password_character': _("Password should be in a character range 6 and 30."),
    }

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean_new_password2(self):
        old_password = self.cleaned_data.get('old_password')
        password = self.cleaned_data.get('new_password1')
        confirm_password = self.cleaned_data.get('new_password2')

        if not password or not confirm_password:
            raise forms.ValidationError(self.error_messages['password_mismatch'])

        if password != confirm_password:
            raise forms.ValidationError(self.error_messages['password_mismatch'])

        if len(password) < 6 or len(password) > 30:
            raise forms.ValidationError(self.error_messages['password_character'])

        if old_password == password:
            raise forms.ValidationError(_('The two password cannot be same.'))
