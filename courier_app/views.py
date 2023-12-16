from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, UpdateView, ListView
from courier_app.filters import *
from admin_app.forms import *
from client_app.models import *
from admin_app.models import *


class ProfilePageView(DetailView):
    model = CustomUser
    template_name = 'courier_app/profile_page.html'
    pk_url_kwarg = 'user_id'
    context_object_name = 'profile'

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PasswordChangePageView(PasswordChangeView):
    template_name = 'courier_app/password_change_page.html'
    form_class = CustomUserPasswordChangeForm
    success_url = reverse_lazy('courier_app:order_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ProfileChangePageView(UpdateView):
    model = CustomUser
    template_name = 'courier_app/profile_change_page.html'
    form_class = CustomUserChangeForm
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('courier_app:order_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.get_success_url())

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OrderListPageView(ListView):
    template_name = 'courier_app/order_list_page.html'
    model = Order
    paginate_by = 5
    context_object_name = 'orders'


class OrderDetailPageView(DetailView):
    template_name = 'courier_app/order_detail_page.html'
    model = Order
    pk_url_kwarg = 'order_id'
    context_object_name = 'order'


@login_required
def my_deliveries(request):
    order_filter = OrderFilter(request.GET, queryset=Order.objects.filter(courier=request.user))
    context = {'order_filter': order_filter}
    return render(request, 'courier_app/my_deliveries_page.html', context)


@login_required
def order_approval(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.courier = request.user
    order.status = 'в процессе доставки'
    order.save()
    return redirect('courier_app:my_deliveries')


@login_required
def order_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'доставлено'
    order.save()
    return redirect('courier_app:my_deliveries')


@login_required
def order_refusal(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.courier = None
    order.status = 'подготовка'
    order.save()
    return redirect('courier_app:order_list')


def is_courier_check(user):
    return user.is_courier
