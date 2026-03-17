document.addEventListener('DOMContentLoaded', () => {

  // Get URLs and CSRF from meta tags
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  const updateUrl = document.querySelector('meta[name="update-cart-url"]').content;
  const removeBaseUrl = document.querySelector('meta[name="remove-item-base-url"]').content;

  // ---------------- Add to Cart ----------------
  document.querySelectorAll(".add-to-cart").forEach(button => {
    button.addEventListener("click", function () {
      const url = this.dataset.url;
      fetch(url, { method: "GET", headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(res => res.json())
        .then(item => {
          if (!item.error) {
            addItemToCart(item);
            const offcanvas = new bootstrap.Offcanvas(document.getElementById('cartOffcanvas'));
            offcanvas.show();
          }
        });
    });
  });

  // ---------------- Add/Update item in cart UI ----------------
  function addItemToCart(item) {
    const cartItems = document.getElementById("cartItems");
    let existing = cartItems.querySelector(`#cart-item-${item.id}`);
    
    if (existing) {
      existing.querySelector('.item-quantity').textContent = item.quantity;
      existing.querySelector('.item-subtotal').textContent = item.subtotal.toFixed(2);
    } else {
      const div = document.createElement("div");
      div.id = `cart-item-${item.id}`;
      div.dataset.itemId = item.id;
      div.dataset.price = item.price;
      div.classList.add("cart-item", "d-flex", "justify-content-between", "align-items-center", "mb-2");

      div.innerHTML = `
        <div class="d-flex align-items-center mb-2">
          <img src="${item.image}" style="width:50px; height:50px; object-fit:contain;" class="me-2">
          <div class="flex-grow-1 d-flex justify-content-between align-items-center">
            <p class="mb-0 small">
              ৳ <span class="item-price">${item.price.toFixed(2)}</span> × 
              <span class="item-quantity">${item.quantity}</span> = 
              ৳ <span class="item-subtotal">${(item.price * item.quantity).toFixed(2)}</span>
            </p>
            <div class="btn-group btn-group-sm ms-4" style="gap: 0.4rem;">
              <button class="btn btn-outline-secondary btn-dec ms-1">-</button>
              <button class="btn btn-outline-secondary btn-inc">+</button>
              <button class="btn btn-danger btn-remove">X</button>
            </div>
          </div>
        </div>
      `;
      cartItems.appendChild(div);
    }

    document.getElementById("cartCount").textContent = item.cart_count;
    document.getElementById("cartTotal").textContent = item.cart_total.toFixed(2);
  }

  // ---------------- Update Quantity ----------------
  function updateCart(itemId, action, cartItemEl) {
    fetch(updateUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ item_id: itemId, action })
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
      headers: { 'X-CSRFToken': csrfToken }
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
  document.getElementById("cartItems").addEventListener("click", e => {
    const cartItem = e.target.closest('.cart-item');
    if (!cartItem) return;

    if (e.target.classList.contains('btn-inc')) updateCart(cartItem.dataset.itemId, 'inc', cartItem);
    if (e.target.classList.contains('btn-dec')) updateCart(cartItem.dataset.itemId, 'dec', cartItem);
    if (e.target.classList.contains('btn-remove')) removeItem(cartItem.dataset.itemId, cartItem);
  });

});