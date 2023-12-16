from django.urls import path
from client_app.views import *

app_name = 'client_app'

urlpatterns = [
    path('', StartPageView.as_view(), name='start_page'),

    path('register_user/', RegisterPageView.as_view(), name='register_page'),
    path('login_user/', LoginPageView.as_view(), name='login_page'),
    path('logout_user/', logout_user, name='logout_user'),
    path('profile/<int:user_id>/', ProfilePageView.as_view(), name='profile_page'),
    path('profile/<int:user_id>/profile_change/', ProfileChangePageView.as_view(), name='profile_change_page'),
    path('profile/<int:user_id>/password_change/', PasswordChangePageView.as_view(), name='password_change_page'),

    path('pharmacy_list/', PharmacyListPageView.as_view(), name='pharmacy_list'),
    path('pharmacy_list/detail/<int:pharmacy_id>/', PharmacyDetailPageView.as_view(), name='pharmacy_detail'),
    path('pharmacy_list/all_location/', all_pharmacy_location, name='all_pharmacy_location'),
    path('pharmacy_list/location/<int:pharmacy_id>/', pharmacy_location, name='pharmacy_location'),

    path('medicine_list/', MedicineListPageView.as_view(), name='medicine_list'),
    path('medicine_list/detail/<slug:medicine_slug>/',
         MedicineDetailPageView.as_view(), name='medicine_detail'),
    path('medicine_list/add_comment/<slug:medicine_slug>/', add_medicine_comment, name='add_medicine_comment'),

    path('comment/<int:comment_id>/like/', like_comment, name='like_comment'),
    path('comment/<int:comment_id>/dislike/', dislike_comment, name='dislike_comment'),
    path('comment/<int:comment_id>/delete/', delete_medicine_comment, name='delete_comment'),

    path('cart/', CartPageView.as_view(), name='cart_page'),
    path('cart/add/<slug:medicine_slug>/', add_product_to_cart, name='cart_add_page'),
    path('cart/remove/<slug:medicine_slug>/', remove_product_from_cart, name='cart_remove_page'),
    path('cart/quantity/<slug:medicine_slug>/<str:param>/', change_quantity, name='cart_quantity_page'),

    path('order/', OrderSavePageView.as_view(), name='order_page'),
    path('order/save/', save_order, name='save_order'),

    path('my_favorites/', my_favorites, name='my_favorites'),
    path('my_favorites/add/<slug:medicine_slug>/', add_favorites, name='add_favorites'),
    path('my_favorites/remove/<int:favorites_id>/', delete_favorites, name='delete_favorites'),

    path('my_deliveries/', my_deliveries, name='my_deliveries'),
    path('my_deliveries/detail/<int:order_id>/', OrderDetailPageView.as_view(), name='order_detail'),
    path('my_deliveries/delete/<int:order_id>/', delete_order, name='delete_order'),
]
