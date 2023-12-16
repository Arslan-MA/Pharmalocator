from django.contrib import admin
from django.contrib.auth.models import Permission
from admin_app.models import *


admin.site.register(Permission)
admin.site.register(CustomUser)
admin.site.register(MedicineCategory)
admin.site.register(TypeMedicine)
admin.site.register(Medicine)
admin.site.register(Pharmacy)
