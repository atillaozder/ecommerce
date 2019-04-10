from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import Group
from .forms import AdminUpdateForm, AdminCreationForm
from .models import Distributor

User = get_user_model()
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = AdminUpdateForm
    add_form = AdminCreationForm
    change_password_form = AdminPasswordChangeForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'email', 'is_active', 'first_name', 'last_name',)
    list_filter = ('is_superuser', 'is_active')
    fieldsets = (
        ('Account Information', {
            'fields': (
                'username',
                'email',
                'password',
                'date_joined',
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'user_permissions',
            )
        }),
        ('Personal Information', {
            'fields': (
                'first_name',
                'last_name',
                'addresses',
                'type',
                'shipping',
                'billing',
                'image',
                'width_field',
                'height_field'
            )
        }),

    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved')
    list_editable = ('is_approved',)
    list_filter = ('is_approved',)
