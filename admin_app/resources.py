from import_export import resources
from admin_app.models import Medicine, Pharmacy


class MedicineResource(resources.ModelResource):
    class Meta:
        model = Medicine


class PharmacyResource(resources.ModelResource):
    class Meta:
        model = Pharmacy
