from django.contrib.auth.decorators import user_passes_test
from django.urls import path
from courier_app.views import *

app_name = 'courier_app'

urlpatterns = [
    path('', OrderListPageView.as_view(), name='order_list'),
    path('order_list/detail/<int:order_id>/', OrderDetailPageView.as_view(), name='order_detail'),
    path('order_list/accept/<int:order_id>/', user_passes_test(is_courier_check)(order_approval),
         name='order_approval'),
    path('order_list/refuse/<int:order_id>/', user_passes_test(is_courier_check)(order_refusal), name='order_refusal'),

    path('profile/<int:user_id>/', ProfilePageView.as_view(), name='profile_page'),
    path('profile/<int:user_id>/profile_change/', ProfileChangePageView.as_view(), name='profile_change_page'),
    path('profile/<int:user_id>/password_change/', PasswordChangePageView.as_view(), name='password_change_page'),

    path('my_deliveries/', user_passes_test(is_courier_check)(my_deliveries),
         name='my_deliveries'),
    path('my_deliveries/delivered/<int:order_id>/', user_passes_test(is_courier_check)(order_delivered),
         name='order_delivered'),
]
