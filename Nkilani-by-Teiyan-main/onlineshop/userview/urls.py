from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'userview'

urlpatterns = [
    path('', views.home_page, name="user-home"),
    path('contact/', views.contact_page, name="contact"),
    path('wishlist/', views.wishlist_page, name="user-wishlist"),
    path('detail/<prodid>/', views.detail_page, name="prod-detail"),
    path('cart/', views.cart_page, name="user-cart"),
    path('shop/', views.shop_page, name="user-shop"),
    path('checkout/', views.checkout_page, name="user-checkout"),
    path("search/", views.search, name="search"),
    path('<str:total_cost>/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('verify-payment/', views.verify_payment, name='verify-payment'),
    path('c2b-mp-pay/', views.lipa_na_mpesa_online, name='c2b-mpesa-transaction'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path("wishlist-items-count", views.wishlist_items_count, name="wishlist-items-count"),
    path("cart-items-count", views.cart_items_count, name="cart-items-count"),
    path("remove-cart-item", views.remove_item_from_cart, name="remove-cart-item"),
    path("remove-wishlist-item", views.remove_item_from_wishlist, name="remove-wishlist-item"),
    path("filter-products", views.filter_products, name="filter-products"),
    path('review/', views.review_product, name='review-product'),
    path('contactus/', views.contactus, name="contactus"),
    path('logout-user/', views.logout_user, name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
