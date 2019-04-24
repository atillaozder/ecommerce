from django.urls import path
from .views import *

app_name = 'products'

urlpatterns = [
    path('distributor/<username>', ProductDistributorListView.as_view(), name='distributor'),
    path('category/<slug>', ProductCategoryListView.as_view(), name='category'),
    path('delete/request', ProductDeleteRequest.as_view(), name="delete_request"),
    path('delete/pending', ProductDeletePendingListView.as_view(), name='delete_pending'),
    path('approve/pending', ProductApprovePendingListView.as_view(), name='approve_pending'),
    path('create', ProductCreateView.as_view(), name="create"),
    path('search', ProductFilterView.as_view(), name='search'),
    path('featured', ProductFeaturedView.as_view(), name='featured'),
    path('<slug>', ProductDetailView.as_view(), name='detail'),
    path('<slug>/add', ProductAddToCartView.as_view(), name='add_to_cart'),
    path('<slug>/remove', ProductRemoveFromCartView.as_view(), name='remove_from_cart'),
    path('<slug>/rate', ProductRateView.as_view(), name='rate'),
    path('<slug>/edit', ProductUpdateView.as_view(), name='update'),
    path('<slug>/delete/', ProductDeleteView.as_view(), name="delete"),
    path('<slug>/approve/', ProductApproveView.as_view(), name='approve'),
    path('<slug>/reject/', ProductRejectView.as_view(), name='reject'),
]