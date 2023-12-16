from django.contrib.auth.decorators import permission_required
from django.urls import path
from admin_app.views import *
from django.contrib.auth.decorators import user_passes_test

app_name = 'admin_app'

urlpatterns = [
    path('', PharmacyListPageView.as_view(), name='pharmacy_list'),
    path('pharmacy_create/', permission_required('is_superuser')(PharmacyCreatePageView.as_view()),
         name='pharmacy_create'),
    path('pharmacy_list/detail/<int:pharmacy_id>/', PharmacyDetailPageView.as_view(), name='pharmacy_detail'),
    path('pharmacy_list/update/<int:pharmacy_id>/', user_passes_test(is_staff_check)(PharmacyUpdatePageView.as_view()),
         name='pharmacy_update'),
    path('pharmacy_list/delete/<int:pharmacy_id>/', permission_required('is_superuser')(
        PharmacyDeletePageView.as_view()), name='pharmacy_delete'),
    path('pharmacy_list/all_location/', all_pharmacy_location, name='all_pharmacy_location'),
    path('pharmacy_list/location/<int:pharmacy_id>/', pharmacy_location, name='pharmacy_location'),

    path('profile/<user_id>/', ProfilePageView.as_view(), name='profile_page'),
    path('profile/<user_id>/profile_change/', ProfileChangePageView.as_view(), name='profile_change_page'),
    path('profile/<user_id>/password_change/', PasswordChangePageView.as_view(), name='password_change_page'),

    path('user_list/', permission_required('is_superuser')(UserListPageView.as_view()), name='user_list_page'),
    path('user_list/detail/<user_id>/', permission_required('is_superuser')(UserDetailPageView.as_view()),
         name='user_detail_page'),
    path('user_list/update/<user_id>/', permission_required('is_superuser')(UserUpdatePageView.as_view()),
         name='user_update_page'),
    path('user_list/delete/<user_id>/', permission_required('is_superuser')(UserDeletePageView.as_view()),
         name='user_delete_page'),

    path('my_pharmacy/', user_passes_test(is_staff_check)(my_pharmacy), name='my_pharmacy'),
    path('my_pharmacy/update/<int:pharmacy_id>/', user_passes_test(is_staff_check)(MyPharmacyUpdatePageView.as_view()),
         name='my_pharmacy_update'),
    path('my_pharmacy/orders_list/<int:pharmacy_id>/', user_passes_test(is_staff_check)(my_pharmacy_orders),
         name='my_pharmacy_orders'),

    path('order/detail/<int:order_id>/', OrderDetailPageView.as_view(), name='order_detail'),
    path('order/accept/<int:order_id>/', user_passes_test(is_staff_check)(order_approval),
         name='order_approval'),
    path('order/refuse/<int:order_id>/', user_passes_test(is_staff_check)(order_refusal), name='order_refusal'),
    path('order/add_comment/<int:order_id>/', add_order_comment, name='add_order_comment'),
    path('order_comment/<int:comment_id>/delete/', delete_order_comment, name='delete_order_comment'),

    path('create_medicines/', user_passes_test(is_staff_check)(MedicineCreatePageView.as_view()),
         name='create_medicines'),
    path('medicine_list/', MedicineListPageView.as_view(), name='medicine_list'),
    path('medicine_list/detail/<slug:medicine_slug>/',
         MedicineDetailPageView.as_view(), name='medicine_detail'),
    path('medicine_list/update/<slug:medicine_slug>/', user_passes_test(is_staff_check)(
        MedicineUpdatePageView.as_view()), name='medicine_update'),
    path('medicine_list/delete/<slug:medicine_slug>/', user_passes_test(is_staff_check)(
        MedicineDeletePageView.as_view()), name='medicine_delete'),
    path('medicine_list/add_comment/<slug:medicine_slug>/', add_medicine_comment, name='add_medicine_comment'),
    path('medicine_comment/<int:comment_id>/delete/', delete_medicine_comment, name='delete_medicine_comment'),

    # path('upload/medicine/', upload_medicine, name='upload_medicine'),
    # path('download/medicine/', download_medicine, name='download_medicine'),
    # path('upload/pharmacy/', upload_pharmacy, name='upload_pharmacy'),
    # path('download/pharmacy/', download_pharmacy, name='download_pharmacy'),

    path('upload/file/', upload_file, name='upload_file'),
    path('download/file/<str:file_type>/', download_file, name='download_file'),
]
