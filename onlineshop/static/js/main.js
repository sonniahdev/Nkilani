(function ($) {
    "use strict";

    // Dropdown on mouse hover
    $(document).ready(function () {
        function toggleNavbarMethod() {
            if ($(window).width() > 992) {
                $('.navbar .dropdown').on('mouseover', function () {
                    $('.dropdown-toggle', this).trigger('click');
                }).on('mouseout', function () {
                    $('.dropdown-toggle', this).trigger('click').blur();
                });
            } else {
                $('.navbar .dropdown').off('mouseover').off('mouseout');
            }
        }
        toggleNavbarMethod();
        $(window).resize(toggleNavbarMethod);
    });


    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({ scrollTop: 0 }, 1500, 'easeInOutExpo');
        return false;
    });


    // Vendor carousel
    $('.vendor-carousel').owlCarousel({
        loop: true,
        margin: 29,
        nav: false,
        autoplay: true,
        smartSpeed: 1000,
        responsive: {
            0: {
                items: 2
            },
            576: {
                items: 3
            },
            768: {
                items: 4
            },
            992: {
                items: 5
            },
            1200: {
                items: 6
            }
        }
    });


    // Related carousel
    $('.related-carousel').owlCarousel({
        loop: true,
        margin: 29,
        nav: false,
        autoplay: true,
        smartSpeed: 1000,
        responsive: {
            0: {
                items: 1
            },
            576: {
                items: 2
            },
            768: {
                items: 3
            },
            992: {
                items: 4
            }
        }
    });


    // Product Quantity
    $('.quantity button').on('click', function () {
        var button = $(this);
        var oldValue = button.parent().parent().find('input').val();
        if (button.hasClass('btn-plus')) {
            var newVal = parseFloat(oldValue) + 1;
        } else {
            if (oldValue > 0) {
                var newVal = parseFloat(oldValue) - 1;
            } else {
                newVal = 0;
            }
        }
        button.parent().parent().find('input').val(newVal);
    });

})(jQuery);

$(document).ready(function () {
    $(".add-to-cart").click(function (e) {
        e.preventDefault();
        var productId = $(this).data("product-id");
        $.ajax({
            url: addToCartURL,
            type: "POST",
            data: {
                csrfmiddlewaretoken: csrfToken,
                product_id: productId
            },
            success: function (response) {
                if (response.success) {
                    // Handle the success response here (e.g., update the cart icon, show a notification).
                } else {
                    // Handle the failure response here (e.g., show an error message).
                    console.error("Error adding to cart: " + response.message);
                    // You can display the error message to the user, for example:
                    // $("#error-message").text("Failed to add to cart: " + response.message);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                // Handle errors (e.g., show an error message).
                console.error("AJAX error: " + textStatus + " - " + errorThrown);
                // You can display a general error message to the user, for example:
                // $("#error-message").text("An error occurred: " + errorThrown);
            }
        });
    });

    $(".add-to-wishlist").click(function (e) {
        e.preventDefault();
        var productId = $(this).data("product-id");
        $.ajax({
            url: "../add-to-wishlist/,
            type: "POST",
            data: {
                csrfmiddlewaretoken: csrfToken,
                product_id: productId
            },
            success: function (response) {
                if (response.success) {
                    // Handle the success response here (e.g., update the wishlist icon, show a notification).
                } else {
                    // Handle the failure response here (e.g., show an error message).
                    console.error("Error adding to wishlist: " + response.message);
                    // You can display the error message to the user, for example:
                    // $("#error-message").text("Failed to add to wishlist: " + response.message);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                // Handle errors (e.g., show an error message).
                console.error("AJAX error: " + textStatus + " - " + errorThrown);
                // You can display a general error message to the user, for example:
                // $("#error-message").text("An error occurred: " + errorThrown);
            }
        });
    });
});


$(document).ready(function () {
  function performSearch(searchText) {
    var isShopPage = window.location.pathname === "/shop/" || window.location.pathname == "/overview/shop/";

    $.ajax({
      url: "{% url 'overview:search' %}",
      type: "POST",
      data: {
        csrfmiddlewaretoken: csrfToken,
        search_input: searchText,
      },
      success: function (response) {
        // Clear the existing content
        $("#page_contents").empty();

        // Append the new products to the page
        if (response.products.length > 0) {
          $.each(response.products, function (index, product) {
            var productHtml = `
              <div class="col-lg-3 col-md-4 col-sm-6 pb-1">
                <!-- Your product HTML here -->
              </div>`;
            $("#page_contents").append(productHtml);
          });
        } else {
          $("#page_contents").html("<p>No products found.</p>");
        }
      },
      error: function () {
        // Handle errors here (e.g., show an error message).
        console.error("AJAX error: Unable to retrieve search results.");
      },
    });
  }

  // Handle the search form submission
  $("form").submit(function (e) {
    e.preventDefault(); // Prevent the form from submitting the traditional way

    var searchText = $(this).find("input[name='search_input']").val();

    performSearch(searchText);
  });
});
