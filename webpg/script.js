document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("product-container");

    // Fetch JSON data
    fetch("fake_store_50_products.json")
        .then(response => response.json())
        .then(data => {
            data.forEach(product => {
                const productCard = document.createElement("div");
                productCard.classList.add("product");

                // Add product details to the card
                productCard.innerHTML = `
                    <img src="${product.image}" alt="${product.title}" class="product-image">
                    <h2>${product.title}</h2>
                    <p><strong>Price: ₹${product.price}</strong></p>
                    <p>Size: ${product.size || 'N/A'} ml</p>
                    <p>Rating: ${product.rating.rate} (${product.rating.count} reviews)</p>

                    <div class="buttons">
                        <button class="buy-btn">Buy Now</button>
                        <button class="cart-btn">Add to Cart</button>
                    </div>
                `;

                // Append product card to the container
                container.appendChild(productCard);
            });
        })
        .catch(error => console.error("Error loading products:", error));
});
