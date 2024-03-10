
var paymentForm = document.getElementById('paymentForm');
paymentForm.addEventListener('submit', payWithPaystack, false);


function payWithPaystack() {
        const email = document.getElementById('email').value;
        const amount = parseFloat(document.getElementById('amount').value) * 100;

        var handler = PaystackPop.setup({
            key: 'pk_test_d394b5ee9580bf2961b1519877d12c6aec20412a',
            email: email,
            amount: amount,
            currency: 'USD',
            ref: 'ref-' + Math.floor((Math.random() * 1000000000) + 1),
            callback: function (response) {
                window.location.href = "/verify-payment/?reference=" + response.reference;
            },
            onClose: function () {
                alert('Payment window closed.');
            }
        });

        handler.openIframe();
    }