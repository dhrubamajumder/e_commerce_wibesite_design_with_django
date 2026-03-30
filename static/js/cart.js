document.addEventListener('DOMContentLoaded', () => {

  // ---------------- Meta & DOM ----------------
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const updateUrl = document.querySelector('meta[name="update-cart-url"]')?.content;
  const removeBaseUrl = document.querySelector('meta[name="remove-item-base-url"]')?.content;
  const cartJsonUrl = document.querySelector('meta[name="cart-json-url"]')?.content;

  const cartItemsContainer = document.getElementById("cartItems");
  const cartCountEl = document.getElementById("cartCount");
  const cartTotalEl = document.getElementById("cartTotal");
  const offcanvasEl = document.getElementById('offcanvasCart');

  // ---------------- Add Item To UI ----------------
  function addItemToCart(item) {

    if (!cartItemsContainer) return;

    let existing = cartItemsContainer.querySelector(`#cart-item-${item.id}`);

    if (existing) {
      existing.querySelector('.item-quantity').textContent = item.quantity;
      existing.querySelector('.item-subtotal').textContent = Number(item.subtotal).toFixed(2);
    } else {

      const div = document.createElement("div");
      div.id = `cart-item-${item.id}`;
      div.dataset.itemId = item.id;
      div.className = "cart-item border-bottom pb-2 mb-2";

      div.innerHTML = `
        <div class="d-flex align-items-center">
          <img src="${item.image}" style="width:50px;height:50px;object-fit:contain;" class="me-2">
          <div class="flex-grow-1">
            <div class="small fw-semibold">${item.name}</div>
            <div class="small">
              ৳ <span class="item-price">${Number(item.price).toFixed(2)}</span> × 
              <span class="item-quantity">${item.quantity}</span> = 
              ৳ <span class="item-subtotal">${Number(item.subtotal).toFixed(2)}</span>
            </div>
          </div>
          <div class="btn-group btn-group-sm ms-2">
            <button class="btn btn-outline-secondary btn-dec">-</button>
            <button class="btn btn-outline-secondary btn-inc">+</button>
            <button class="btn btn-danger btn-remove">×</button>
          </div>
        </div>
      `;

      cartItemsContainer.appendChild(div);
    }

    if (cartCountEl) cartCountEl.textContent = item.cart_count;
    if (cartTotalEl) cartTotalEl.textContent = Number(item.cart_total).toFixed(2);
  }

  // ---------------- Update Quantity ----------------
  function updateCart(itemId, action, cartItemEl) {

    if (!updateUrl || !csrfToken) return;

    fetch(updateUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ item_id: itemId, action })
    })
    .then(res => res.json())
    .then(data => {

      if (data.status === 'success') {

        if (data.quantity <= 0) {
          cartItemEl.remove();
        } else {
          cartItemEl.querySelector('.item-quantity').textContent = data.quantity;
          cartItemEl.querySelector('.item-subtotal').textContent = Number(data.subtotal).toFixed(2);
        }

        if (cartCountEl) cartCountEl.textContent = data.cart_count;
        if (cartTotalEl) cartTotalEl.textContent = Number(data.cart_total).toFixed(2);
      }
    });
  }

  // ---------------- Remove Item ----------------
  function removeItem(itemId, cartItemEl) {

    if (!removeBaseUrl || !csrfToken) return;

    const url = removeBaseUrl.replace('0', itemId);

    fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken }
    })
    .then(res => res.json())
    .then(data => {

      if (data.status === 'success') {
        cartItemEl.remove();

        if (cartCountEl) cartCountEl.textContent = data.cart_count;
        if (cartTotalEl) cartTotalEl.textContent = Number(data.cart_total).toFixed(2);
      }
    });
  }

  // ---------------- Event Delegation ----------------
  if (cartItemsContainer) {
    cartItemsContainer.addEventListener("click", e => {

      const cartItem = e.target.closest('.cart-item');
      if (!cartItem) return;

      const itemId = cartItem.dataset.itemId;

      if (e.target.classList.contains('btn-inc'))
        updateCart(itemId, 'inc', cartItem);

      if (e.target.classList.contains('btn-dec'))
        updateCart(itemId, 'dec', cartItem);

      if (e.target.classList.contains('btn-remove'))
        removeItem(itemId, cartItem);
    });
  }

  // ---------------- Load Cart On Page Load ----------------
  function loadCart() {

    if (!cartJsonUrl) return;

    fetch(cartJsonUrl)
      .then(res => res.json())
      .then(data => {

        if (!cartItemsContainer) return;

        cartItemsContainer.innerHTML = "";

        data.items.forEach(item => addItemToCart(item));
      });
  }

  loadCart();

  // ---------------- Add To Cart Button ----------------
  document.querySelectorAll(".add-to-cart").forEach(button => {

    button.addEventListener("click", function () {

      const url = this.dataset.url;

      fetch(url)
        .then(res => res.json())
        .then(data => {

          addItemToCart(data);

          if (offcanvasEl) {
            const offcanvas = new bootstrap.Offcanvas(offcanvasEl);
            offcanvas.show();
          }
        })
        .catch(err => console.error("Cart Error:", err));
    });

  });

});