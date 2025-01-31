$(document).ready(function () {
    $(".add-to-cart").click(function (e) {
        e.preventDefault();
        let itemID = $(this).data("id");
        let itemType = $(this).data("type");  // "plan" or "service"

        $.ajax({
            url: `/cart/add/${itemID}/${itemType}/`,
            type: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            },
            success: function (response) {
                if (response.cart_count !== undefined) {
                    $("#cart-count").text(response.cart_count);
                    
                    // Show success toast notification
                    var toast = new bootstrap.Toast($('#cartToast')[0]);
                    toast.show();
                }
            },
            error: function () {
                alert("Error adding item to cart.");
            }
        });
    });
});


 // Show or hide promo code field based on checkbox
 document.getElementById('applyPromoCode').addEventListener('change', function() {
    const promoCodeField = document.getElementById('promoCodeField');
    if (this.checked) {
        promoCodeField.style.display = 'block';
    } else {
        promoCodeField.style.display = 'none';
    }
});

// Handling the order placement (replace with actual functionality)
document.getElementById('placeOrderBtn').addEventListener('click', function() {
    const fullName = document.getElementById('FullName').value;
    const promoCode = document.getElementById('PromoCode').value;
    // Do something with order details like sending them to the backend
    alert('Order placed for: ' + fullName + (promoCode ? ' with Promo Code: ' + promoCode : ''));
});
