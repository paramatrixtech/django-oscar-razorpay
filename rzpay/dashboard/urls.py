from django.urls import path, re_path
from . import views

urlpatterns = [
    path('transaction/', views.TransactionListView.as_view(),
         name='razorpay-transaction-list'),
    re_path(r'^transaction/(?P<pk>\d+)/$',
            views.TransactionDetailView.as_view(), 
            name='razorpay-transaction-detail'),
]
