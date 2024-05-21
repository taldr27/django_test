from django.urls import path
from .views import (
    ProductView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductUploadImageView
)

urlpatterns = [
    path('products/all', ProductView.as_view(), name='products'),
    path('products/create', ProductCreateView.as_view(), name='product-create'),
    path('products/update/<int:pk>', ProductUpdateView.as_view(), name='product-update'),
    path('products/delete/<int:pk>', ProductDeleteView.as_view(), name='product-delete'),
    path('products/upload-image', ProductUploadImageView.as_view(), name='product-upload-image')
]
