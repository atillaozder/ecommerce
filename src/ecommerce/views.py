from django.views.generic import View
from django.shortcuts import render
from category.models import Category


class HomeView(View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {
            'categories': categories
        }
        return render(request, 'home.html', context)
