import base64
import json
from datetime import datetime

import requests
from decouple import config
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
from django_daraja.views import stk_push_callback_url

from .models import *
from mpesa.core import MpesaClient
from adminview.models import Product, ProductImage, ProductProperties
from userview.models import Review, Order, OrderItem
from django.contrib.auth.models import User

from userview.models import TransactionDetails, PaymentResponse, TransactionResult


def remove_media_root(file_paths):
    media_root = settings.MEDIA_ROOT
    len_mr = len(media_root)

    return file_paths[len_mr + 1:]


def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)

        cart = request.COOKIES.get('cart', '{}')
        cart = json.loads(cart)

        cart[str(product_id)] = cart.get(str(product_id), 0) + 1

        response = JsonResponse({'success': True, 'message': 'Product added to cart'})
        response.set_cookie('cart', json.dumps(cart))

        return response
    return redirect("/")


def add_to_wishlist(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")

        product = get_object_or_404(Product, id=product_id)

        wishlist = request.COOKIES.get('wishlist', '{}')
        wishlist = json.loads(wishlist)

        wishlist[str(product_id)] = product.name

        response = JsonResponse({'success': True, 'message': 'Product added to wishlist'})
        response.set_cookie('wishlist', json.dumps(wishlist))
        return response
    return redirect("/")


def count_cart_items(request):
    cart = request.COOKIES.get('cart', '{}')
    cart = json.loads(cart)
    total_items = sum(cart.values())
    return JsonResponse({'total_items': total_items})


def count_wishlist_items(request):
    wishlist = request.COOKIES.get('wishlist', '{}')
    wishlist = json.loads(wishlist)
    total_items = len(wishlist)
    return JsonResponse({'total_items': total_items})


def landing_page(request):
    products = Product.objects.all()

    context = {"products": products}
    return render(request, "main/overview.html", context)


def cart_view(request):
    cart = request.COOKIES.get('cart', '{}')
    cart = json.loads(cart)

    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        total_price += product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity})
    print("Cart Data from Cookies:", cart)
    print("Cart Items:", cart_items)
    print(total_price)

    return render(request, "main/cart-prev.html", {'cart_items': cart_items, 'total_price': total_price})


def wishlist_page(request):
    wishlist = request.COOKIES.get('wishlist', '{}')
    wishlist = json.loads(wishlist)

    wishlist_items = []
    for product_id, product_name in wishlist.items():
        product = get_object_or_404(Product, id=product_id)
        wishlist_items.append({'product': product, 'product_name': product_name})

    return render(request, "main/wishlist-prev.html", {'wishlist_items': wishlist_items})


def contact_page(request):
    return render(request, "main/contact-prev.html")


def checkout_page(request):
    cart = request.COOKIES.get('cart', '{}')
    cart = json.loads(cart)

    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    total_with_shipping = str(int(total_price + 10))

    return render(request, "main/checkout-prev.html", {'cart_items': cart_items, 'total_price': total_with_shipping})


def detail_page(request, prodid):
    product = get_object_or_404(Product, id=prodid)
    try:
        product_properties = ProductProperties.objects.get(product=product)
    except ProductProperties.DoesNotExist:
        product_properties = None

    print(f"Product: {product}")

    reviews = Review.objects.filter(product=product)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'product_properties': product_properties,
        'reviews': reviews,
        'related_products': related_products,
    }
    return render(request, "main/detail-prev.html", context)


def shop_page(request):
    products = Product.objects.all()
    context = {"products": products}

    return render(request, "main/shop-prev.html", context)


def signin_page(request):
    return render(request, "main/Sign in.html")


def signup_page(request):
    return render(request, "main/Sign Up.html")


def register(request):
    if request.method == "POST":
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            error_message = "Email already exists. Please use a different email."
            return render(request, 'Sign In.html', {'error_message': error_message})

        try:
            print("signing in user")
            user = User.objects.create_user(username=email, email=email, password=password)
            customer = Customers.objects.create(user=user, first_name=firstname, last_name=lastname)
            print(user.id)
            customer.save()

            signin_url = reverse('overview:signin')
            return redirect(signin_url)
        except IntegrityError:
            error_message = "An error occurred during registration. Please try again."
            return render(request, 'main/sign up.html', {'error_message': error_message})

    return render(request, 'main/Sign up.html')


def filter_products(request):
    if request.method == "POST":
        selected_prices = request.POST.getlist("price_category")
        selected_colors = request.POST.getlist("color_category")
        selected_sizes = request.POST.getlist("size_category")

        filters = {}
        filtered_products = Product.objects.all()

        if selected_prices:
            price_ranges = []
            for selected_price in selected_prices:
                if selected_price == "price_category1":
                    price_ranges.append((0, 100))
                elif selected_price == "price_category2":
                    price_ranges.append((100, 200))
                elif selected_price == "price_category3":
                    price_ranges.append((200, 300))
                elif selected_price == "price_category4":
                    # Use a very large number instead of 'inf'
                    price_ranges.append((300, 1e9))
            if price_ranges:
                price_q = Q()
                for price_range in price_ranges:
                    price_q |= Q(price__range=price_range)
                filtered_products = filtered_products.filter(price_q)

        if selected_colors:
            filters["productproperties__colors__name__in"] = selected_colors

        if selected_sizes:
            filters["productproperties__sizes__name__in"] = selected_sizes

        if not selected_prices and not selected_colors and not selected_sizes:
            filtered_products = Product.objects.all()

        data = [
            {
                "id": product.id,
                "image": product.image,
                "name": product.name,
                "price": product.price,
                "color": ", ".join(product.productproperties_set.first().colors.values_list("name", flat=True)) if product.productproperties_set.exists() else None,
                "size": ", ".join(product.productproperties_set.first().sizes.values_list("name", flat=True)) if product.productproperties_set.exists() else None
            }
            for product in filtered_products
        ]

        return render(request, "main/shop-prev.html", {"products": data})

    return redirect("overview:shop-prev")


def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            admin_user = AdminAccounts.objects.get(email=email)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
                admin_url = reverse('adminview:admin-home')
                return redirect(admin_url)
            else:
                return JsonResponse({'error': 'Incorrect Email or Password'}, status=400)
        except AdminAccounts.DoesNotExist:
            try:
                user = authenticate(request, username=email, password=password)
                customer = Customers.objects.get(user=user)
                if user is not None:
                    auth_login(request, user)
                    customer_url = reverse('userview:user-home')
                    return redirect(customer_url)
                else:
                    return JsonResponse({'error': 'Incorrect Email or Password'}, status=400)
            except Customers.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

    return render(request, 'main/Sign in.html')


def newsletter(request):
    if request.method == "POST":
        email = request.POST.get("newsletter_email")
        print("<" + "-"*20 + "email:" + email)

        Newsletter.objects.create(email=email).save()
    return redirect("/")


def search(request):
    if request.method == "POST":
        text = request.POST.get("search_input")
        products = Product.objects.filter(name__icontains=text)
    else:
        products = []

    return render(request, "main/shop-prev.html", {"products": products})


def delete_cart_item(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        print(f"item found {product_id}")

        cart = request.COOKIES.get('cart', '{}')
        cart = json.loads(cart)

        if str(product_id) in cart:
            del cart[str(product_id)]

            response = JsonResponse({'success': True, 'message': 'Product removed from cart'})
            response.set_cookie('cart', json.dumps(cart))
            return response
        else:
            return JsonResponse({'success': False, 'message': 'Product not found in cart'})

    return HttpResponse(status=405)


def clear_cart(request):
    cart = request.COOKIES.get('cart', '{}')
    cart = json.loads(cart)

    list = [i for i in cart]
    for i in list:
        del cart[i]

    response = JsonResponse({'success': True, 'message': 'Products removed from cart'})
    response.set_cookie('cart', json.dumps(cart))
    return response


def delete_wishlist_item(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")

        wishlist = request.COOKIES.get('wishlist', '{}')
        wishlist = json.loads(wishlist)

        if str(product_id) in wishlist:
            del wishlist[str(product_id)]

            response = JsonResponse({'success': True, 'message': 'Product removed from wishlist'})
            response.set_cookie('wishlist', json.dumps(wishlist))
            return response
        else:
            return JsonResponse({'success': False, 'message': 'Product not found in wishlist'})

    return HttpResponse(status=405)


def submit_pay_details(request, total_price):
    if request.method == "POST":
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('number')
        total = total_price

        response = lipa_na_mpesa_online(request, phone, total, firstname)

        return HttpResponse(response)
    return redirect("overview:checkout-prev")


def lipa_na_mpesa_online(request, number, total_amount, name):
    # cl = MpesaClient()
    # access_token = cl.access_token()
    # api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    # headers = {"Authorization": "Bearer %s" % access_token}
    #
    # BusinessShortCode = config('MPESA_EXPRESS_SHORTCODE')
    #
    # timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # passkey = config('MPESA_PASSKEY')
    # password = base64.b64encode((BusinessShortCode + passkey + timestamp).encode('ascii')).decode('utf-8')
    #
    # PartyA = str(number)[1:]
    # print(number)
    # print(PartyA)
    # PartyB = BusinessShortCode
    # PhoneNumber = PartyA
    # AccountReference = f"{name}"
    # TransactionDesc = "Testing stk push"
    #
    # request_data = {
    #     "BusinessShortCode": BusinessShortCode,
    #     "Password": password,
    #     "Timestamp": timestamp,
    #     "TransactionType": "CustomerBuyGoodsOnline",
    #     "Amount": total_amount,
    #     "PartyA": PartyA,
    #     "PartyB": PartyB,
    #     "PhoneNumber": PhoneNumber,
    #     "CallBackURL": stk_push_callback_url,
    #     "AccountReference": AccountReference,
    #     "TransactionDesc": TransactionDesc
    # }
    #
    # resp = requests.post(api_url, json=request_data, headers=headers)
    # print(resp)
    #
    # if resp.status_code == 200 or resp.json().get('ResponseCode') == '0':
    #     order = Order.objects.create(
    #         customer=None,
    #         total_amount=total_amount,
    #         payment_reference=resp.json().get('MerchantRequestID'),
    #         payment_status=True
    #     )
    #     cart = request.COOKIES.get('cart', '{}')
    #     cart = json.loads(cart)
    #
    #     for product_id, quantity in cart.items():
    #         product = get_object_or_404(Product, id=product_id)
    #         total_price = product.price * quantity
    #
    #         order_item = OrderItem.objects.create(
    #             order=order,
    #             product=product,
    #             quantity=quantity,
    #             total_price=total_price
    #         )

    clear_cart(request)
    print(clear_cart(request))

    return clear_cart(request)


def handle_payment_response(request):
    response_data = request.POST

    payment_response = PaymentResponse.objects.create(
        merchant_request_id=response_data['MerchantRequestID'],
        checkout_request_id=response_data['CheckoutRequestID'],
        response_code=response_data['ResponseCode'],
        response_description=response_data['ResponseDescription'],
        customer_message=response_data['CustomerMessage']
    )

    if response_data['ResponseCode'] == '0':
        transaction_result = TransactionResult.objects.create(
            payment_response=payment_response,
            result_code=response_data['ResultCode'],
            result_description=response_data['ResultDesc']
        )

        TransactionDetails.objects.create(
            transaction_result=transaction_result,
            amount=response_data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'],
            mpesa_receipt_number=response_data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'],
            transaction_date=response_data['Body']['stkCallback']['CallbackMetadata']['Item'][2]['Value'],
            phone_number=response_data['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value']
        )

    return HttpResponse("Payment response processed successfully")
