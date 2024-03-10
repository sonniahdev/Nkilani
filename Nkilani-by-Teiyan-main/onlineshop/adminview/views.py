from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from PIL import Image
import os

from .models import *
from main.models import ContactUs, Newsletter
from userview.models import Order, OrderItem, Review


def admin_page(request):
    user = request.user

    products = Product.objects.all()
    context = {"user": user, "products": products}
    return render(request, "adminview/home_page.html", context)


def subscritions_page(request):
    subs = Newsletter.objects.all()
    context = {"subscriptions": subs}
    return render(request, "adminview/subscriptions.html", context)


def orders_page(request):
    orders = Order.objects.all()
    context = {"orders": orders}
    return render(request, "adminview/orders.html", context)


def messages_page(request):
    messages = ContactUs.objects.all()
    context = {"messages": messages}
    return render(request, "adminview/messages.html", context)


def remove_featured_product(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "adminview/add-to-featured.html", context)


def add_featured_product(request):
    products = Product.objects.all()
    context = {"products": products}

    return render(request, "adminview/add-to-featured.html", context)


def edit_product_details(request, prodid):
    product = Product.objects.get(id=prodid)
    context = {"product": product}

    return render(request, "adminview/edit-product.html", context)


def update_product(request, prodid):
    try:
        product = Product.objects.get(id=prodid)

        if request.method == "POST":
            name = request.POST.get("product_name")
            description = request.POST.get("product_description")
            price = request.POST.get("product_price")
            quantity = request.POST.get("product_quantity")

            product.name = name
            product.description = description
            product.price = price
            product.quantity = quantity
            product.save()

            return redirect("adminview:admin-home")

    except Product.DoesNotExist:
        return redirect("adminview:admin-home")


def delete_product(request, prodid):
    try:
        product = Product.objects.get(id=prodid)
        product.delete()
        return redirect("adminview:admin-home")

    except Product.DoesNotExist:
        return redirect("adminview:admin-home")


def add_featured(request, prodid):
    product = Product.objects.get(id=prodid)

    FeaturedProduct.objects.create(product=product)
    return redirect("adminview:admin-home")


def create_offer(request, prodid):
    product = Product.objects.get(id=prodid)

    OfferedProduct.objects.create(product=product)
    return redirect("adminview:admin-home")


def add_product(request, user):
    if request.method == "POST":
        name = request.POST.get('product_name')
        description = request.POST.get('product_description')
        image = request.FILES.get('product_image')
        price = request.POST.get('product_price')
        category = request.POST.get('product_category')

        if Product.objects.filter(name=name).exists():
            error_message = "Product with this name already exists. Please use a different name."
            return render(request, 'admin section.html', {'error_message': error_message})

        default_path = "My Products"
        fs = FileSystemStorage()
        file_path = os.path.join(settings.MEDIA_ROOT, default_path, image.name)
        fs.save(file_path, image)

        img = Image.open(file_path)
        img.thumbnail((550, 700), Image.Resampling.LANCZOS)
        img.save(file_path)

        Product.objects.create(name=name, description=description, image=os.path.join(default_path, image.name),
                               price=price, category=category)

    return render(request, 'adminview/admin section.html')


def logout_user(request):
    try:
        logout(request)
        return redirect('overview:landing_page')
    except:
        return redirect('overview:landing_page')
