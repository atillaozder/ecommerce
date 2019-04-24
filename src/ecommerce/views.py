from django.views.generic import View
from django.shortcuts import render
from category.models import Category
from product.models import Product


class HomeView(View):

    def get(self, request):
        context = {
            'categories': Category.objects.all(),
            'recent': Product.objects.all().recent(),
            'featured': Product.objects.all().featured()
        }
        return render(self.request, 'home.html', context)
