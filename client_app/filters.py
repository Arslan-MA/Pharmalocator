import django_filters
from client_app.models import *


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = ['pharmacy', 'address', 'status']

    def __init__(self, *args, **kwargs):
        super(OrderFilter, self).__init__(*args, **kwargs)
        self.filters['pharmacy'].label = "Аптека"
        self.filters['address'].label = "Адрес клиента"
        self.filters['status'].label = "Статус заказа"
