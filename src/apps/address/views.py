from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from .models import Address
from .forms import AddressForm


class AddressCreateView(LoginRequiredMixin, CreateView):
    template_name = 'address_form.html'
    form_class = AddressForm

    def get(self, request, *args, **kwargs):
        """
            check user if customer render page
            Args:
                request:logged in user
            Returns:
                rendered page for the address form
            Raises:
        """
        if not request.user.type == 'customer':
            raise Http404
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    def form_valid(self, form):
        valid = super(AddressCreateView, self).form_valid(form)
        if valid:
            user = self.request.user
            address = form.instance
            user.addresses.add(address)
            user.save()
        return valid

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'username': self.request.user.username})


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'address_form.html'
    form_class = AddressForm

    def get_object(self):
        id = self.kwargs.get('pk')
        instance = get_object_or_404(Address, pk=id)
        return instance

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'username': self.request.user.username})


class AddressDeleteView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        id = self.request.POST.get('id')
        instance = get_object_or_404(Address, pk=id)
        instance.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
