from django.urls import path, include
from .views import *

app_name = 'products'

urlpatterns = [
    path('delete/request', ProductDeleteRequest.as_view(), name="delete_request"),
    path('approve/pending', ProductApprovePendingListView.as_view(), name='approve_pending'),
    path('create', ProductCreateView.as_view(), name="create"),
    path('<slug>', ProductDetailView.as_view(), name='detail'),
    path('<slug>/edit', ProductUpdateView.as_view(), name='update'),
    path('<slug>/delete', ProductDeleteView.as_view(), name="delete"),
    path('<slug>/approve', ProductApproveView.as_view(), name='approve'),
    path('<slug>/reject', ProductRejectView.as_view(), name='reject'),
]