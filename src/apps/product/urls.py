from django.urls import path, include
from .views import *

app_name = 'products'

urlpatterns = [
    path('delete/request', ProductDeleteRequest.as_view(), name="delete_request"),
    path('delete/pending', ProductDeletePendingListView.as_view(), name='delete_pending'),
    path('approve/pending', ProductApprovePendingListView.as_view(), name='approve_pending'),
    path('create', ProductCreateView.as_view(), name="create"),
    path('<slug>', ProductDetailView.as_view(), name='detail'),
    path('<slug>/add', ProductAddToCartView.as_view(), name='add_to_cart'),
    path('<slug>/remove', ProductRemoveFromCartView.as_view(), name='remove_from_cart'),
    path('<slug>/rate', ProductRateView.as_view(), name='rate'),
    path('<slug>/edit', ProductUpdateView.as_view(), name='update'),
    path('<slug>/delete/', ProductDeleteView.as_view(), name="delete"),
    path('<slug>/approve/', ProductApproveView.as_view(), name='approve'),
    path('<slug>/reject/', ProductRejectView.as_view(), name='reject'),
]