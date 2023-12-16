import django_filters
from client_app.models import *
from admin_app.models import *


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone', 'is_staff', 'is_courier']

    def __init__(self, *args, **kwargs):
        super(UserFilter, self).__init__(*args, **kwargs)
        self.filters['name'].label = "Имя пользователя"
        self.filters['email'].label = "Электронная почта"
        self.filters['phone'].label = "Номер телефона"
        self.filters['is_staff'].label = "Статус фармацевт"
        self.filters['is_courier'].label = "Статус курьер"


class PharmacyFilter(django_filters.FilterSet):
    class Meta:
        model = Pharmacy
        fields = ['name', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        super(PharmacyFilter, self).__init__(*args, **kwargs)
        self.filters['name'].label = "Название"
        self.filters['phone'].label = "Номер телефона"
        self.filters['address'].label = "Адрес"


class MyPharmacyOrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = ['address', 'status']

    def __init__(self, *args, **kwargs):
        super(MyPharmacyOrderFilter, self).__init__(*args, **kwargs)
        self.filters['address'].label = "Адрес клиента"
        self.filters['status'].label = "Статус заказа"


class MedicineFilter(django_filters.FilterSet):
    price = django_filters.NumberFilter(label='Точная цена:')
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt', label='Цены больше указанной')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt', label='Цены меньше указанной')

    class Meta:
        model = Medicine
        fields = ['title', 'medicinal_category', 'type_medicine', 'age_category', 'price']

    def __init__(self, *args, **kwargs):
        super(MedicineFilter, self).__init__(*args, **kwargs)
        self.filters['title'].label = "Название"
        self.filters['medicinal_category'].label = "Категория лекарства"
        self.filters['type_medicine'].label = "Тип лекарства"
        self.filters['age_category'].label = "Возрастная категория"
