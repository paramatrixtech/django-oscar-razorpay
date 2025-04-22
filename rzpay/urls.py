from django.urls import path, re_path
from . import views

urlpatterns = [
    # Use re_path for patterns with regular expressions
    re_path(r'^preview/(?P<basket_id>\d+)/$',
            views.SuccessResponseView.as_view(),
            name='razorpay-success-response'),

    re_path(r'^cancel/(?P<basket_id>\d+)/$',
            views.CancelResponseView.as_view(),
            name='razorpay-cancel-response'),

    # Use path for simpler URL patterns
    path('payment/', views.PaymentView.as_view(), name='razorpay-payment'),
]
