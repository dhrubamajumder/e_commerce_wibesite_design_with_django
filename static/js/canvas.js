document.addEventListener('DOMContentLoaded', () => {

  // ---------------- Get Config ----------------
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  const updateUrl = document.querySelector('meta[name="update-cart-url"]').content;
  const removeBaseUrl = document.querySelector('meta[name="remove-item-url"]').content;

  const cartItems = document.getElementById("cartItems");

  if (!cartItems) return; // safety

  // ---------------- Add to Cart ----------------
  document.querySelectorAll(".add-to-cart").forEach(button => {
    button.addEventListener("click", function () {
      const url = this.dataset.url;

      fetch(url, {
        method: "GET",
        headers: {"X-Requested-With": "XMLHttpRequest"}
      })
      .then(res => res.json())
      .then(item => {
        if (!item.error) {
          addItemToCart(item);

          const offcanvas = new bootstrap.Offcanvas(document.getElementById('offcanvasCart'));
          offcanvas.show();
        }
      });
    });
  });

  // ---------------- Add Item UI ----------------
  function addItemToCart(item) {
    let existing = document.getElementById(`cart-item-${item.id}`);

    if (existing) {
      existing.querySelector('.item-quantity').textContent = item.quantity;
      existing.querySelector('.item-subtotal').textContent = item.subtotal.toFixed(2);
    } else {
      const div = document.createElement("div");
      div.id = `cart-item-${item.id}`;
      div.dataset.itemId = item.id;
      div.classList.add("cart-item", "mb-2");

      div.innerHTML = `
        <div class="d-flex align-items-center">
          <img src="${item.image}" style="width:50px;height:50px" class="me-2">

          <div class="flex-grow-1 d-flex justify-content-between align-items-center">
            <p class="mb-0 small">
              ৳ <span class="item-price">${item.price.toFixed(2)}</span> × 
              <span class="item-quantity">${item.quantity}</span> = 
              ৳ <span class="item-subtotal">${(item.price * item.quantity).toFixed(2)}</span>
            </p>

            <div class="btn-group btn-group-sm ms-3">
              <button class="btn btn-outline-secondary btn-dec">-</button>
              <button class="btn btn-outline-secondary btn-inc">+</button>
              <button class="btn btn-danger btn-remove">X</button>
            </div>
          </div>
        </div>
      `;

      cartItems.appendChild(div);
    }

    updateCartUI(item);
  }

  // ---------------- Update Cart API ----------------
  function updateCart(itemId, action, cartItemEl) {

    fetch(updateUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({item_id: itemId, action})
    })
    .then(res => res.json())
    .then(data => {

      if (data.status === 'success') {

        if (data.quantity <= 0) {
          cartItemEl.remove();
        } else {
          cartItemEl.querySelector('.item-quantity').textContent = data.quantity;
          cartItemEl.querySelector('.item-subtotal').textContent = data.subtotal.toFixed(2);
        }

        document.getElementById('cartCount').textContent = data.cart_count;
        document.getElementById('cartTotal').textContent = data.cart_total.toFixed(2);
      }
    });
  }

  // ---------------- Remove Item ----------------
  function removeItem(itemId, cartItemEl) {

    fetch(`${removeBaseUrl}${itemId}/`, {
      method: 'POST',
      headers: {'X-CSRFToken': csrfToken}
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        cartItemEl.remove();

        document.getElementById('cartCount').textContent = data.cart_count;
        document.getElementById('cartTotal').textContent = data.cart_total.toFixed(2);
      }
    });
  }

  // ---------------- Event Delegation ----------------
  cartItems.addEventListener("click", e => {

    const cartItem = e.target.closest('.cart-item');
    if (!cartItem) return;

    const itemId = cartItem.dataset.itemId;

    if (e.target.classList.contains('btn-inc')) {
      updateCart(itemId, 'inc', cartItem);
    }

    if (e.target.classList.contains('btn-dec')) {
      updateCart(itemId, 'dec', cartItem);
    }

    if (e.target.classList.contains('btn-remove')) {
      removeItem(itemId, cartItem);
    }

  });

});


// ------------------------------------------------
// ------------------------------------------------
// ------------------------------------------------

const searchInput = document.getElementById('search-input');
const resultsBox = document.getElementById('search-results');

searchInput.addEventListener('keyup', function() {
    let query = this.value;

    if (query.length < 1) {
        resultsBox.innerHTML = "";
        return;
    }

    fetch(`/ajax-search/?q=${query}`)
        .then(response => response.json())
        .then(data => {

            let html = "";

            data.products.forEach(product => {
                html += `
                    <a href="/product/${product.id}/" class="d-block p-2 border-bottom text-dark text-decoration-none">
                        <div class="d-flex align-items-center">
                            <img src="${product.image}" width="40" class="me-2">
                            <div>
                                <div>${product.name}</div>
                                <small>৳ ${product.price}</small>
                            </div>
                        </div>
                    </a>
                `;
            });

            resultsBox.innerHTML = html;
        });
});

