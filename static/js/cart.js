document.addEventListener('DOMContentLoaded', () => {

  // ---------------- Meta & DOM Elements ----------------
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const updateUrl = document.querySelector('meta[name="update-cart-url"]')?.content;
  const removeBaseUrl = document.querySelector('meta[name="remove-item-base-url"]')?.content;
  const cartJsonUrl = document.querySelector('meta[name="cart-json-url"]')?.content;

  const cartItemsContainer = document.getElementById("cartItems");
  const cartCountEl = document.getElementById("cartCount");
  const cartTotalEl = document.getElementById("cartTotal");
  const offcanvasEl = document.getElementById('offcanvasCart');

  // ---------------- Add Item to Cart UI ----------------
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
      div.classList.add("cart-item", "d-flex", "justify-content-between", "align-items-center", "mb-2");

      div.innerHTML = `
        <div class="d-flex align-items-center mb-2 w-100">
          <img src="${item.image}" style="width:50px; height:50px; object-fit:contain;" class="me-2">
          <div class="flex-grow-1 d-flex justify-content-between align-items-center">
            <p class="mb-0 small">
              ৳ <span class="item-price">${Number(item.price).toFixed(2)}</span> × 
              <span class="item-quantity">${item.quantity}</span> = 
              ৳ <span class="item-subtotal">${Number(item.subtotal).toFixed(2)}</span>
            </p>
            <div class="btn-group btn-group-sm ms-4" style="gap: 0.4rem;">
              <button class="btn btn-outline-secondary btn-dec">-</button>
              <button class="btn btn-outline-secondary btn-inc">+</button>
              <button class="btn btn-danger btn-remove">X</button>
            </div>
          </div>
        </div>
      `;
      cartItemsContainer.appendChild(div);
    }

    if (cartCountEl && item.cart_count !== undefined)
      cartCountEl.textContent = item.cart_count;

    if (cartTotalEl && item.cart_total !== undefined)
      cartTotalEl.textContent = Number(item.cart_total).toFixed(2);
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

    const url = removeBaseUrl.replace('/0/', `/${itemId}/`);

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

  // ---------------- Event Delegation for Cart Buttons ----------------
  if (cartItemsContainer) {
    cartItemsContainer.addEventListener("click", e => {
      const cartItem = e.target.closest('.cart-item');
      if (!cartItem) return;

      if (e.target.classList.contains('btn-inc'))
        updateCart(cartItem.dataset.itemId, 'inc', cartItem);

      if (e.target.classList.contains('btn-dec'))
        updateCart(cartItem.dataset.itemId, 'dec', cartItem);

      if (e.target.classList.contains('btn-remove'))
        removeItem(cartItem.dataset.itemId, cartItem);
    });
  }

  // ---------------- Load Cart on Page Reload ----------------
  function loadCartOnPageLoad() {
    if (!cartJsonUrl || !cartItemsContainer) return;

    fetch(cartJsonUrl)
      .then(res => res.json())
      .then(data => {
        cartItemsContainer.innerHTML = "";

        data.items.forEach(item => {
          addItemToCart({
            ...item,
            cart_total: data.cart_total,
            cart_count: data.cart_count
          });
        });

        if (cartTotalEl)
          cartTotalEl.textContent = Number(data.cart_total).toFixed(2);
        if (cartCountEl)
          cartCountEl.textContent = data.cart_count;

        // ---------------- Show Offcanvas AFTER items added ----------------
        if (data.cart_count > 0) {
          const offcanvasElReload = document.getElementById('offcanvasCart');
          if (offcanvasElReload) {
            const offcanvasInstanceReload = new bootstrap.Offcanvas(offcanvasElReload);
            offcanvasInstanceReload.show();
          }
        }
      });
  }

  loadCartOnPageLoad();

  // ---------------- Add to Cart Buttons ----------------
  document.querySelectorAll(".add-to-cart").forEach(button => {
    document.addEventListener("DOMContentLoaded", function () {

      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function () {

          const productId = this.dataset.id;
          const url = this.dataset.url;

          fetch(url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrftoken,
              "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({
              item_id: productId,
              action: "inc"
            })
          })
          .then(res => res.json())
          .then(data => {

            if (data.status === "success") {

              addItemToCart(data);

              if (offcanvasEl) {
                const offcanvasInstanceClick = new bootstrap.Offcanvas(offcanvasEl);
                offcanvasInstanceClick.show();
              }
            }
          })
          .catch(error => {
            console.error("Cart error:", error);
          });

        });
      });

    });
  });

});

