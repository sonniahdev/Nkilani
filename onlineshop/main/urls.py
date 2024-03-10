from django.urls import path
from . import views

app_name = "overview"

urlpatterns = [
    path('', views.landing_page, name="landing_page"),
    path('contact', views.contact_page, name="info"),
    path('<int:prodid>/detail', views.detail_page, name="detail-prev"),
    path('cart', views.cart_view, name="cart-prev"),
    path('wishlist', views.wishlist_page, name="wishlist-prev"),
    path('shop', views.shop_page, name="shop-prev"),
    path('checkout', views.checkout_page, name="checkout-prev"),
    path('signin', views.signin_page, name="signin"),
    path('signup', views.signup_page, name="signup"),
    path('login-user', views.login, name="login"),
    path('register-user', views.register, name="register"),
    path('newsletter', views.newsletter, name="get-newsletter"),
    path('search', views.search, name="search"),
    path('add-to-cart', views.add_to_cart, name="add-to-cart"),
    path('add-to-wishlist', views.add_to_wishlist, name="add-to-wishlist"),
    path('cart-items-count', views.count_cart_items, name="cart-items-count"),
    path('delete-cart-item', views.delete_cart_item, name="delete_cart_item"),
    path("wishlist-items-count", views.count_wishlist_items, name="wishlist-items-count"),
    path("payment-response", views.handle_payment_response, name="payment-response"),
    path("filter-products", views.filter_products, name="filter-products"),
    path("<str:total_price>/pay", views.submit_pay_details, name="submit_pay_details")
]

