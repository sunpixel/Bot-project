document.addEventListener('DOMContentLoaded', async () => {
    const cartId = window.CART_ID;
    const cartItemsDiv = document.getElementById('cart-items');
    const emptyCartDiv = document.getElementById('empty-cart');
    const itemCountSpan = document.getElementById('item-count');
    const totalPriceSpan = document.getElementById('total-price');
    const checkoutBtn = document.getElementById('checkout-btn');

    async function fetchCart() {
        try {
            const response = await fetch(`/cart/${cartId}`);
            const result = await response.json();
            const items = result.data || [];

            cartItemsDiv.innerHTML = '';
            if (items.length === 0) {
                emptyCartDiv.style.display = 'block';
                itemCountSpan.textContent = '0 items';
                totalPriceSpan.textContent = '$0.00';
                checkoutBtn.disabled = true;
                cartItemsDiv.appendChild(emptyCartDiv);
                return;
            }

            emptyCartDiv.style.display = 'none';
            let total = 0;
            items.forEach(([name, qty, product_id]) => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'tg-cart-item';
                itemDiv.innerHTML = `
                    <span class="tg-cart-item-name">${name}</span>
                    <div class="tg-cart-controls">
                        <button class="tg-btn tg-btn-dec" data-id="${product_id}">-</button>
                        <span class="tg-cart-item-qty" id="qty-${product_id}">${qty}</span>
                        <button class="tg-btn tg-btn-inc" data-id="${product_id}">+</button>
                        <button class="tg-btn tg-btn-del" data-id="${product_id}">&#128465;</button>
                    </div>
                `;
                cartItemsDiv.appendChild(itemDiv);
                total += qty;
            });

            itemCountSpan.textContent = `${items.length} item${items.length > 1 ? 's' : ''}`;
            totalPriceSpan.textContent = `Total: ${total}`;
            checkoutBtn.disabled = false;

            // Add event listeners for buttons
            document.querySelectorAll('.tg-btn-inc').forEach(btn => {
                btn.onclick = async () => {
                    const id = btn.getAttribute('data-id');
                    await updateQuantity(id, 1);
                };
            });
            document.querySelectorAll('.tg-btn-dec').forEach(btn => {
                btn.onclick = async () => {
                    const id = btn.getAttribute('data-id');
                    await updateQuantity(id, -1);
                };
            });
            document.querySelectorAll('.tg-btn-del').forEach(btn => {
                btn.onclick = async () => {
                    const id = btn.getAttribute('data-id');
                    await deleteItem(id);
                };
            });
        } catch (err) {
            cartItemsDiv.innerHTML = '<div class="tg-empty-cart"><p>Failed to load cart.</p></div>';
            itemCountSpan.textContent = '0 items';
            totalPriceSpan.textContent = '$0.00';
            checkoutBtn.disabled = true;
        }
    }

    async function updateQuantity(productId, delta) {
        // Get current quantity
        const qtySpan = document.getElementById(`qty-${productId}`);
        let qty = parseInt(qtySpan.textContent, 10) + delta;
        if (qty < 1) return; // Don't allow less than 1
        await fetch(`/cart/${cartId}/update`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({product_id: productId, quantity: qty})
        });
        fetchCart();
    }

    async function deleteItem(productId) {
        await fetch(`/cart/${cartId}/item/${productId}`, {
            method: 'DELETE'
        });
        fetchCart();
    }

    checkoutBtn.addEventListener('click', async () => {
        checkoutBtn.disabled = true;
        checkoutBtn.textContent = 'Processing...';
        try {
            const response = await fetch(`/buy/${cartId}`, { method: 'POST' });
            const result = await response.json();
            alert(`Total price: ${result.total.toFixed(2)}`);
        } catch (err) {
            alert('Checkout failed!');
        }
        checkoutBtn.disabled = false;
        checkoutBtn.textContent = 'Proceed to Checkout';
    });

    fetchCart();
});