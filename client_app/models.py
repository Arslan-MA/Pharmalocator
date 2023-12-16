from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from admin_app.models import *
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    total_price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.name} - {self.total_price}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartitems')
    product = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, related_name='items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.title} - {self.quantity}"

    def increase_quantity(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.quantity += 1
        self.cart.total_price += self.product.price
        self.cart.save()
        super().save(force_insert, force_update, using, update_fields)

    def decrease_quantity(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.quantity -= 1
        self.cart.total_price -= self.product.price
        self.cart.save()
        super().save(force_insert, force_update, using, update_fields)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk:
            original_quantity = CartItem.objects.get(pk=self.pk).quantity
            if original_quantity != self.quantity:
                quantity_difference = self.quantity - original_quantity
                price_difference = quantity_difference * self.product.price
                self.cart.total_price += price_difference
        else:
            self.cart.total_price += self.product.price * self.quantity

        self.cart.save()
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.cart.total_price -= self.product.price * self.quantity
        self.cart.save()
        return super().delete(using, keep_parents)

    def get_item_price(self):
        if self.product:
            return self.product.price * self.quantity
        return 0


class Order(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    products_string = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    courier = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name='courier',
                                blank=True, null=True)
    total_price = models.PositiveIntegerField()

    STATUS_CHOICES = [
        ('проверка', 'проверка'),
        ('отказано', 'отказано'),
        ('подготовка', 'подготовка'),
        ('в процессе доставки', 'в процессе доставки'),
        ('доставлено', 'доставлено'),
    ]

    status = models.CharField(max_length=255, choices=STATUS_CHOICES)

    def get_absolute_url(self):
        return reverse('order_id', args=(self.pk,))

    def __str__(self):
        return f"{self.client.name} - {self.client.phone} - {self.total_price} - {self.status}"


class OrderComment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Order, on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    likes = GenericRelation(Like)
    dislike = GenericRelation(Dislike)

    def __str__(self):
        return f"{self.user.name} - {self.subject}"


class Favorites(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Medicine, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name} - {self.product.title}"
