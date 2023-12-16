from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django_filters.views import FilterView
from tablib import Dataset
from admin_app.forms import *
from admin_app.filters import *
from client_app.forms import *
from client_app.models import *
from admin_app.models import *
from .resources import MedicineResource, PharmacyResource
from django.http import HttpResponse
import folium
from import_export.formats import base_formats
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import zipfile


class ProfilePageView(DetailView):
    model = CustomUser
    template_name = 'admin_app/profile_page.html'
    pk_url_kwarg = 'user_id'
    context_object_name = 'profile'

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        if user.is_staff and not user.is_superuser:
            pharmacy = Pharmacy.objects.get(pharmacist=user)
            context['pharmacy'] = pharmacy
        return context


@login_required(login_url='/login_user/')
def my_pharmacy(request):
    pharmacy = Pharmacy.objects.get(pharmacist=request.user)
    context = {'pharmacy': pharmacy}
    return render(request, 'admin_app/my_pharmacy_page.html', context)


@login_required(login_url='/login_user/')
def my_pharmacy_orders(request, pharmacy_id):
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)

    if request.user == pharmacy.pharmacist:
        order_filter = MyPharmacyOrderFilter(request.GET, queryset=Order.objects.filter(pharmacy=pharmacy))
        context = {'orders': order_filter}
        return render(request, 'admin_app/my_pharmacy_orders.html', context)


class PasswordChangePageView(PasswordChangeView):
    template_name = 'admin_app/password_change_page.html'
    form_class = CustomUserPasswordChangeForm
    success_url = reverse_lazy('admin_app:pharmacy_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ProfileChangePageView(UpdateView):
    model = CustomUser
    template_name = 'admin_app/profile_change_page.html'
    form_class = CustomUserChangeForm
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('admin_app:pharmacy_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.get_success_url())

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PharmacyCreatePageView(CreateView):
    template_name = 'admin_app/pharmacy_create_page.html'
    model = Pharmacy
    form_class = PharmacyModelForm
    success_url = reverse_lazy('admin_app:medicine_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PharmacyListPageView(FilterView):
    template_name = 'admin_app/pharmacy_list_page.html'
    model = Pharmacy
    filterset_class = PharmacyFilter
    paginate_by = 5
    context_object_name = 'pharmacies'


class PharmacyDetailPageView(DetailView):
    template_name = 'admin_app/pharmacy_detail_page.html'
    model = Pharmacy
    pk_url_kwarg = 'pharmacy_id'
    context_object_name = 'pharmacy'


class MyPharmacyUpdatePageView(UpdateView):
    template_name = 'admin_app/pharmacy_update_page.html'
    model = Pharmacy
    form_class = MyPharmacyModelForm
    pk_url_kwarg = 'pharmacy_id'
    success_url = reverse_lazy('admin_app:pharmacy_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PharmacyUpdatePageView(UpdateView):
    template_name = 'admin_app/pharmacy_update_page.html'
    model = Pharmacy
    form_class = PharmacyModelForm
    pk_url_kwarg = 'pharmacy_id'
    success_url = reverse_lazy('admin_app:pharmacy_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PharmacyDeletePageView(DeleteView):
    template_name = 'admin_app/pharmacy_delete_page.html'
    model = Pharmacy
    pk_url_kwarg = 'pharmacy_id'
    success_url = reverse_lazy('admin_app:pharmacy_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class MedicineCreatePageView(CreateView):
    template_name = 'admin_app/medicine_create_page.html'
    model = Medicine
    form_class = MedicineModelForm
    success_url = reverse_lazy('admin_app:medicine_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class MedicineListPageView(FilterView):
    template_name = 'admin_app/medicine_list_page.html'
    model = Medicine
    filterset_class = MedicineFilter
    paginate_by = 5
    context_object_name = 'medicines'


class MedicineDetailPageView(DetailView):
    template_name = 'admin_app/medicine_detail_page.html'
    model = Medicine
    slug_url_kwarg = 'medicine_slug'
    context_object_name = 'medicine'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['pharmacies'] = Pharmacy.objects.all()
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
            return redirect('admin_app:medicine_detail', medicine_slug=medicine_slug)


@login_required(login_url='/login_user/')
def delete_medicine_comment(request, comment_id):
    comment = MedicineComment.objects.get(pk=comment_id)
    medicine_slug = comment.subject.slug
    comment.delete()
    return redirect('admin_app:medicine_detail', medicine_slug=medicine_slug)


class MedicineUpdatePageView(UpdateView):
    template_name = 'admin_app/medicine_update_page.html'
    model = Medicine
    form_class = MedicineModelForm
    slug_url_kwarg = 'medicine_slug'
    success_url = reverse_lazy('admin_app:medicine_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class MedicineDeletePageView(DeleteView):
    template_name = 'admin_app/medicine_delete_page.html'
    model = Medicine
    slug_url_kwarg = 'medicine_slug'
    success_url = reverse_lazy('admin_app:medicine_list')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class UserListPageView(FilterView):
    template_name = 'admin_app/user_list_page.html'
    model = CustomUser
    filterset_class = UserFilter
    paginate_by = 5
    context_object_name = 'customusers'


class UserDetailPageView(DetailView):
    template_name = 'admin_app/user_detail_page.html'
    model = CustomUser
    pk_url_kwarg = 'user_id'
    context_object_name = 'customuser'


class UserUpdatePageView(UpdateView):
    template_name = 'admin_app/user_update_page.html'
    model = CustomUser
    form_class = CustomUserAdminCreationForm
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('admin_app:user_list_page')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class UserDeletePageView(DeleteView):
    template_name = 'admin_app/user_delete_page.html'
    model = CustomUser
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('admin_app:user_list_page')

    @method_decorator(login_required(login_url='/login_user/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OrderDetailPageView(DetailView):
    template_name = 'admin_app/order_detail_page.html'
    model = Order
    pk_url_kwarg = 'order_id'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = OrderComment.objects.filter(subject=self.object)
        context['comment_form'] = OrderCommentModelForm()
        return context


@login_required(login_url='/login_user/')
def add_order_comment(request, order_id):
    if request.method == 'POST':
        user = request.user
        order = get_object_or_404(Order, pk=order_id)
        form = OrderCommentModelForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = user
            comment.subject = order
            comment.save()
            return redirect('admin_app:order_detail', order_id=order_id)


@login_required(login_url='/login_user/')
def delete_order_comment(request, comment_id):
    comment = OrderComment.objects.get(pk=comment_id)
    order_id = comment.subject.pk
    comment.delete()
    return redirect('admin_app:order_detail', order_id=order_id)


@login_required(login_url='/login_user/')
def order_approval(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    pharmacy_id = order.pharmacy.pk
    order.status = 'подготовка'
    order.save()
    return redirect('admin_app:my_pharmacy_orders', pharmacy_id=pharmacy_id)


@login_required(login_url='/login_user/')
def order_refusal(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    pharmacy_id = order.pharmacy.pk
    order.status = 'отказано'
    order.save()
    return redirect('admin_app:my_pharmacy_orders', pharmacy_id=pharmacy_id)


def is_staff_check(user):
    return user.is_staff


def upload_file(request):
    if request.method == 'POST':
        file_format = request.FILES['file'].name.split('.')[-1]
        data_type = request.POST['type']

        dataset = Dataset()
        imported_data = dataset.load(request.FILES['file'].read(), format=file_format)

        if data_type == 'medicine':
            resource = MedicineResource()
            result = resource.import_data(dataset, dry_run=True)  # Проверка на ошибки
            if not result.has_errors():
                resource.import_data(dataset, dry_run=False)  # Загрузка данных
                return redirect('admin_app:medicine_list')
            else:
                return HttpResponse('Произошла ошибка при загрузке данных')
        elif data_type == 'pharmacy':
            resource = PharmacyResource()
            result = resource.import_data(dataset, dry_run=True)  # Проверка на ошибки
            if not result.has_errors():
                resource.import_data(dataset, dry_run=False)  # Загрузка данных
                return redirect('admin_app:pharmacy_list')
            else:
                return HttpResponse('Произошла ошибка при загрузке данных')
        else:
            return HttpResponse('Неподдерживаемый тип данных')

    return render(request, 'admin_app/upload_file.html')


def download_file(request, file_type):
    if file_type == 'medicine':
        dataset = MedicineResource().export()
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="medicine.xls"'

        response_json = HttpResponse(dataset.json, content_type='application/json')
        response_json['Content-Disposition'] = 'attachment; filename="medicine.json"'

        # Создаем ZIP-архив
        archive = zipfile.ZipFile('medicine_files.zip', 'w')
        archive.writestr('medicine.xls', response.content)
        archive.writestr('medicine.json', response_json.content)
        archive.close()

        # Отправляем ZIP-архив пользователю
        with open('medicine_files.zip', 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="medicine_files.zip"'

        return response
    elif file_type == 'pharmacy':
        dataset = PharmacyResource().export()
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="pharmacy.xls"'

        response_json = HttpResponse(dataset.json, content_type='application/json')
        response_json['Content-Disposition'] = 'attachment; filename="pharmacy.json"'

        # Создаем ZIP-архив
        archive = zipfile.ZipFile('pharmacy_files.zip', 'w')
        archive.writestr('pharmacy.xls', response.content)
        archive.writestr('pharmacy.json', response_json.content)
        archive.close()

        # Отправляем ZIP-архив пользователю
        with open('pharmacy_files.zip', 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="pharmacy_files.zip"'

        return response
    else:
        return HttpResponse('Неверный тип файла')


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

    return render(request, 'admin_app/all_pharmacy_location.html', {'map': map._repr_html_(),
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
    return render(request, 'admin_app/pharmacy_location.html', {'map': map._repr_html_(),
                                                                'pharmacy': pharmacy})
