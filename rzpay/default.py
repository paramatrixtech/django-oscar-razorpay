from django.templatetags.static import static
from django.urls import reverse_lazy
from django.conf import settings

RZ_IS_TIMEOUT = getattr(
    settings, "RZ_IS_TIMEOUT", "True"
),
RZ_VENDOR_LOGO = getattr(
    settings, "RZ_VENDOR_LOGO", static('store-logo.png')
),
RZ_THEME_COLOR = getattr(
    settings, "RZ_THEME_COLOR", "#F37254"
),
RZ_TIMEOUT = getattr(
    settings, "RZ_TIMEOUT", "900"
) # In seconds
RZ_SHIPPING_METHOD_FAILURE_URL = getattr(
    settings, "RZ_SHIPPING_METHOD_FAILURE_URL",
    reverse_lazy('checkout:shipping-method')
)
RZ_BASKET_SUMMARY_FAILURE_URL = getattr(
    settings, "RZ_BASKET_SUMMARY_FAILURE_URL",
    reverse_lazy('basket:summary')
)
RZ_SHIPPING_ADDRESS_FAILURE_URL = getattr(
    settings, "RZ_SHIPPING_ADDRESS_FAILURE_URL",
    reverse_lazy('checkout:shipping-address')
)
RZ_SUCCESS_URL = getattr(
    settings, "RZ_SUCCESS_URL", reverse_lazy('checkout:thank-you')
)