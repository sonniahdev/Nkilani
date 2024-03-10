from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=100, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0,)
    image = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.name


class FeaturedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateField()
    duration = models.PositiveIntegerField()

    def __str__(self):
        return self.product.name


class OfferedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateField()
    duration = models.PositiveIntegerField()
    percentage_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.15)

    def __str__(self):
        return self.product.name


class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    image_path = models.CharField(max_length=1000)

    def __str__(self):
        return self.product.name + " - " + str(self.id)


class Size(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProductProperties(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    sizes = models.ManyToManyField(Size, blank=True)
    colors = models.ManyToManyField(Color, blank=True)

    def __str__(self):
        return self.product.name + " - " + str(self.id)
