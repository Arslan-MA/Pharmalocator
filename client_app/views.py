from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render, get_object_or_404
from django.urls import resolve
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView, UpdateView, ListView, CreateView, FormView
from django_filters.views import FilterView
import folium
from import_export.formats import base_formats
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from admin_app.forms import *
from client_app.forms import *
from client_app.filters import *
from admin_app.filters import *
from client_app.models import *
from admin_app.models import *


class StartPageView(TemplateView):
    template_name = 'client_app/start_page.html'


class RegisterPageView(CreateView):
    template_name = 'client_app/register_page.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('client_app:start_page')

    def form_valid(self, form):
        super().form_valid(form)
        user = form.instance
        cart = Cart()
        cart.user = user
        cart.save()
        user = form.save()
        login(self.request, user)
        return redirect(self.get_success_url())


class LoginPageView(LoginView):
    template_name = 'client_app/login_page.html'
    form_class = CustomUserAuthenticationForm
    next_page = reverse_lazy('client_app:start_page')

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('admin_app:pharmacy_list')
        elif self.request.user.is_courier:
            return reverse_lazy('courier_app:order_list')
        else:
            return super().get_success_url()


@login_required(login_url='/login_user/')
def logout_user(request):
    logout(request)
    return redirect('client_app:start_page')


class ProfilePageView(DetailView):
    model = CustomUser
    template_name = 'client_app/profile_page.html'
    pk_url_kwarg = 'user_id'
    context_object_name = 'profile'

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CartPageView(ListView):
    model = Cart
    template_name = 'client_app/cart_page.html'
    context_object_name = 'cart'

    def get_queryset(self):
        cart = get_object_or_404(Cart, user=self.request.user)
        return cart

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='/login_user/')
def add_product_to_cart(request, medicine_slug):
    product = get_object_or_404(Medicine, slug=medicine_slug)
    cart = get_object_or_404(Cart, user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    current_url = resolve(request.path_info).url_name
    return redirect('client_app:medicine_list')


@login_required(login_url='/login_user/')
def change_quantity(request, medicine_slug, param):
    product = get_object_or_404(Medicine, slug=medicine_slug)
    cart_item = get_object_or_404(CartItem, product=product)

    if param == 'incr':
        cart_item.increase_quantity()
    if param == 'decr':
        cart_item.decrease_quantity()

    return redirect('client_app:cart_page')


@login_required(login_url='/login_user/')
def remove_product_from_cart(request, medicine_slug):
    product = get_object_or_404(Medicine, slug=medicine_slug)
    cart_item = get_object_or_404(CartItem, product=product)

    cart_item.delete()

    return redirect('client_app:cart_page')


@login_required(login_url='/login_user/')
def save_order(request):
    if request.method == 'POST':
        pharmacy_id = request.POST.get('pharmacy')
        address = request.POST.get('address')
        if pharmacy_id and address:
            cart = get_object_or_404(Cart, user=request.user)
            pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
            total_price = cart.total_price

            order = Order.objects.create(client=request.user, pharmacy=pharmacy, address=address,
                                         total_price=total_price, status='проверка')

            order.products_string = "".join([f"<p>Название: {cart_item.product.title}<br>"
                                             f"Категория лекарства: {cart_item.product.medicinal_category}<br>"
                                             f"Тип лекарства: {cart_item.product.type_medicine}<br>"
                                             f"Возрастная категория: {cart_item.product.age_category}<br>"
                                             f"Количество: {cart_item.quantity}</p><br>"
                                             for cart_item in cart.cartitems.all()])
            order.save()

            cart.cartitems.all().delete()
            cart.total_price = 0
            cart.save()

            return redirect('client_app:medicine_list')
    return redirect('client_app:order_page')


class PasswordChangePageView(PasswordChangeView):
    template_name = 'client_app/password_change_page.html'
    form_class = CustomUserPasswordChangeForm
    success_url = reverse_lazy('client_app:start_page')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ProfileChangePageView(UpdateView):
    model = CustomUser
    template_name = 'client_app/profile_change_page.html'
    form_class = CustomUserChangeForm
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('client_app:start_page')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.get_success_url())

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PharmacyListPageView(FilterView):
    template_name = 'client_app/pharmacy_list_page.html'
    model = Pharmacy
    filterset_class = PharmacyFilter
    paginate_by = 5
    context_object_name = 'pharmacies'


class PharmacyDetailPageView(DetailView):
    template_name = 'client_app/pharmacy_detail_page.html'
    model = Pharmacy
    pk_url_kwarg = 'pharmacy_id'
    context_object_name = 'pharmacy'


class MedicineListPageView(FilterView):
    template_name = 'client_app/medicine_list_page.html'
    model = Medicine
    filterset_class = MedicineFilter
    paginate_by = 5
    context_object_name = 'medicines'


class MedicineDetailPageView(DetailView):
    template_name = 'client_app/medicine_detail_page.html'
    model = Medicine
    slug_url_kwarg = 'medicine_slug'
    context_object_name = 'medicine'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = Favorites.objects.filter(product=self.object)
        context['comments'] = MedicineComment.objects.filter(subject=self.object)
        context['comment_form'] = MedicineCommentModelForm()
        return context


@login_required(login_url='/login_user/')
def add_medicine_comment(request, medicine_slug):
    if request.method == 'POST':
        user = request.user
        medicine = get_object_or_404(Medicine, slug=medicine_slug)
        form = MedicineCommentModelForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = user
            comment.subject = medicine
            comment.save()
            return redirect('client_app:medicine_detail', medicine_slug=medicine_slug)


@login_required(login_url='/login_user/')
def delete_medicine_comment(request, comment_id):
    comment = MedicineComment.objects.get(pk=comment_id)
    medicine_slug = comment.subject.slug
    comment.delete()
    return redirect('client_app:medicine_detail', medicine_slug=medicine_slug)


class OrderSavePageView(FormView):
    template_name = 'client_app/order_page.html'
    form_class = OrderModelForm


class OrderDetailPageView(DetailView):
    template_name = 'client_app/order_detail_page.html'
    model = Order
    pk_url_kwarg = 'order_id'
    context_object_name = 'order'

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = OrderComment.objects.filter(subject=self.object)
        context['comment_form'] = OrderModelForm()
        return context


@login_required(login_url='/login_user/')
def delete_order(request, order_id):
    Order.objects.filter(id=order_id).delete()
    return redirect('client_app:my_deliveries')


@login_required(login_url='/login_user/')
def my_favorites(request):
    favorites = Favorites.objects.filter(user=request.user)
    context = {'favorites': favorites}
    return render(request, 'client_app/my_favorites_page.html', context)


@login_required(login_url='/login_user/')
def add_favorites(request, medicine_slug):
    medicine = get_object_or_404(Medicine, slug=medicine_slug)
    Favorites.objects.get_or_create(user=request.user, product=medicine)
    return redirect('client_app:my_favorites')


@login_required(login_url='/login_user/')
def delete_favorites(request, favorites_id):
    favorites = Favorites.objects.get(pk=favorites_id)
    favorites.delete()
    return redirect('client_app:my_favorites')


@login_required(login_url='/login_user/')
def my_deliveries(request):
    order_filter = OrderFilter(request.GET, queryset=Order.objects.filter(client=request.user))
    context = {'order_filter': order_filter}
    return render(request, 'client_app/my_deliveries_page.html', context)


@login_required(login_url='/login_user/')
def like_comment(request, comment_id):
    user = request.user
    comment = get_object_or_404(MedicineComment, pk=comment_id)
    like, created = Like.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(MedicineComment),
        object_id=comment.id,
        user=user
    )
    try:
        dislike = Dislike.objects.get(
            content_type=ContentType.objects.get_for_model(MedicineComment),
            object_id=comment.id,
            user=user
        )
        dislike.delete()
    except Dislike.DoesNotExist:
        pass
    if created or like.disliked:
        like.disliked = False
        like.save()
        medicine_slug = comment.subject.slug
        return redirect('client_app:medicine_detail', medicine_slug=medicine_slug)
    else:
        like.delete()
        medicine_slug = comment.subject.slug
        return redirect('client_app:medicine_detail', medicine_slug=medicine_slug)


@login_required(login_url='/login_user/')
def dislike_comment(request, comment_id):
    user = request.user
    comment = get_object_or_404(MedicineComment, pk=comment_id)
    dislike, created = Dislike.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(MedicineComment),
        object_id=comment.id,
        user=user
    )
    try:
        like = Like.objects.get(
            content_type=ContentType.objects.get_for_model(MedicineComment),
            object_id=comment.id,
            user=user
        )
        like.delete()
    except Like.DoesNotExist:
        pass
    if created or not dislike.liked:
        dislike.liked = True
        dislike.save()
        medicine_slug = comment.subject.slug
        return redirect('client_app:medicine_detail', medicine_slug=medicine_slug)
    else:
        dislike.delete()
        medicine_slug = comment.subject.slug
        return redirect('client_app:medicine_detail', medicine_slug=medicine_slug)


def all_pharmacy_location(request):
    pharmacies = Pharmacy.objects.all()
    geolocator = Nominatim(user_agent="pharmacy_locator")
    map = folium.Map(location=[41.2995, 69.2401], zoom_start=12)

    for pharmacy in pharmacies:
        location = geolocator.geocode(pharmacy.address)
        folium.Marker([location.latitude, location.longitude], popup=pharmacy.name).add_to(map)

    user_location = request.POST.get('user_location')
    if user_location:
        user_address = geolocator.geocode(user_location)
        folium.Marker([user_address.latitude, user_address.longitude],
                      icon=folium.Icon(color='green')).add_to(map)
        for pharmacy in pharmacies:
            location = geolocator.geocode(pharmacy.address)
            distance = geodesic((user_address.latitude, user_address.longitude), (
                location.latitude, location.longitude)).km
            pharmacy.distance = round(distance, 2)

    return render(request, 'client_app/all_pharmacy_location.html', {'map': map._repr_html_(),
                                                                     'pharmacies': pharmacies})


def pharmacy_location(request, pharmacy_id):
    pharmacy = Pharmacy.objects.get(pk=pharmacy_id)
    geolocator = Nominatim(user_agent="pharmacy_locator")
    location = geolocator.geocode(pharmacy.address)
    map = folium.Map(location=[location.latitude, location.longitude], zoom_start=15)

    user_location = request.POST.get('user_location')
    if user_location:
        user_address = geolocator.geocode(user_location)
        folium.Marker([user_address.latitude, user_address.longitude],
                      icon=folium.Icon(color='green')).add_to(map)

        location = geolocator.geocode(pharmacy.address)
        distance = geodesic((user_address.latitude, user_address.longitude), (
            location.latitude, location.longitude)).km
        pharmacy.distance = round(distance, 2)

    folium.Marker([location.latitude, location.longitude], popup=pharmacy.name).add_to(map)
    return render(request, 'client_app/pharmacy_location.html', {'map': map._repr_html_(),
                                                                 'pharmacy': pharmacy})
