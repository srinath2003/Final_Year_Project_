let allProducts = [];
let categoryToBrands = {}; // Store brands per category
let selectedBrands = new Set(); // Track selected brands

async function fetchProducts() {
    let response = await fetch('/jsonproducts');
    let products = await response.json();
    allProducts = products; // Store the products.
    displayProducts(products);
    populateFilters(products);
}

fetchProducts();

// Search Bar Functionality
document.getElementById('searchBar').addEventListener('input', function () {
    let searchQuery = this.value.toLowerCase();

    let filteredProducts = allProducts.filter(product => {
        return product.Name.toLowerCase().includes(searchQuery) ||
               product.Category.toLowerCase().includes(searchQuery) ||
               product.Brand.toLowerCase().includes(searchQuery);
    });

    displayProducts(filteredProducts);
});

// Populate Category Dropdown & Brand Checkboxes
function populateFilters(products) {
    let categorySet = new Set();
    let brandSet = new Set();

    products.forEach(product => {
        categorySet.add(product.Category);
        brandSet.add(product.Brand);
    });

    let categoryDropdown = document.getElementById('categoryFilter');
    categorySet.forEach(category => {
        let option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryDropdown.appendChild(option);
    });

    let brandDropdown = document.getElementById('brandFilter');
    brandSet.forEach(brand => {
        let label = document.createElement('label');
        label.innerHTML = `<input type="checkbox" value="${brand}"> ${brand}`;
        brandDropdown.appendChild(label);

        // Add event listener to each checkbox
        label.querySelector('input').addEventListener('change', function() {
            if (this.checked) {
                selectedBrands.add(brand);
            } else {
                selectedBrands.delete(brand);
            }
            applyFilters(); // Apply filters immediately after checkbox change
        });
    });
}

// Apply Filters
function applyFilters() {
    let selectedCategory = document.getElementById('categoryFilter').value;
    let selectedBrandsArray = Array.from(selectedBrands);
    let minPrice = document.getElementById('minPrice').value;
    let maxPrice = document.getElementById('maxPrice').value;
    let rating= document.getElementById('rating').value;
    
    let filteredProducts = allProducts.filter(product => {
        return (!selectedCategory || product.Category === selectedCategory) &&
            (selectedBrandsArray.length === 0 || selectedBrandsArray.includes(product.Brand)) &&
            (!minPrice || product.Price >= parseFloat(minPrice)) &&
            (!maxPrice || product.Price <= parseFloat(maxPrice)) &&
            (!rating || product.Rating >= parseFloat(rating));
    });

    displayProducts(filteredProducts);
}


// Display Products
function displayProducts(products) {
    let container = document.getElementById('productContainer');
    container.innerHTML = '';

    products.forEach(product => {
        let productCard = document.createElement('div');
        productCard.classList.add('product-card');

        productCard.innerHTML = `
            <img src="${product.Image}" alt="${product.Name}">
            <h2>${product.Name}</h2>
            <p><strong>Category:</strong> ${product.Category}</p>
            <p><strong>Brand:</strong> ${product.Brand}</p>
            <p><strong>Price:</strong> ₹${product.Price}</p>
            <p><strong>Stock Left:</strong> ${product.Stock_Quantity}</p>
            <p><strong>Rating:</strong> ⭐${product.Rating} (${product.Rating_Count} reviews)</p>
                        <div class="product-buttons">
                       <a href="/product/${product.ID}" class="view-details" onclick="logAndNavigate(event, '${product.ID}', '${product.Category}', this)">View Details</a>

                        <button class="add-to-cart" onclick="logInteraction('${product.ID}', 'add_to_cart', this, '${product.Category}');addToCart(${product.ID}, '${product.Name}', ${product.Price})">Add to Cart</button>
                        <button class="like" onclick="logInteraction('${product.ID}', 'like', this, '${product.Category}')">❤️ Like</button>
                    </div>
        `;

        container.appendChild(productCard);
    });
}
//log and view details
function logAndNavigate(event, productId, category, element) {
    event.preventDefault(); // Prevent immediate navigation

    logInteraction(productId, 'view_details', element, category);

    // Delay navigation slightly to ensure the log request is sent
    setTimeout(() => {
        window.location.href = element.href;
    }, 300); // Adjust the delay as needed
}

  // Function to fetch user and session IDs (Replace with actual retrieval logic)
  function getUserId() {
    return "2b3a32b7-c4cc-4513-98ab-85fca793b02c"; // Hardcoded or replace with dynamic retrieval
}

function getSessionId() {
    return "9a84470c-4ed1-4546-991d-cf24ad957c77"; // Hardcoded or replace with dynamic retrieval
}

        // Log interaction (click events)
        function logInteraction(productId, action, button, category = "Unknown") {
            const userId = getUserId();
            const sessionId = getSessionId();

            fetch('/log_interaction', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    product_id: productId,
                    user_id: userId,
                    session_id: sessionId,
                    action: action,
                    category: category,
                    action_timestamp: new Date().toISOString()
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Server Response:', data);
                button.innerText = action === 'add_to_cart' ? '✅ Added to Cart' : '❤️ Liked';
                button.disabled = true;  // Disable button after clicking
            })
            .catch(error => console.error('Error:', error));
        }

// Add event listeners to the other filters.
document.getElementById('categoryFilter').addEventListener('change', applyFilters);
document.getElementById('minPrice').addEventListener('change', applyFilters);
document.getElementById('maxPrice').addEventListener('change', applyFilters);

// CART FUNCTIONALITY
function addToCart(id, name, price) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    // Check if the product already exists in the cart
    let existingProduct = cart.find(item => item.id === id);
    if (existingProduct) {
        existingProduct.quantity += 1; // Increase quantity
    } else {
        cart.push({ id, name, price, quantity: 1 }); // Add new product
    }

    localStorage.setItem("cart", JSON.stringify(cart));
    updateCartCount();
    alert("Product added to cart!");
}

// Function to load cart items in cart.html
function loadCart() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartContainer = document.getElementById("cartContainer");

    if (cart.length === 0) {
        cartContainer.innerHTML = "<p>Your cart is empty.</p>";
        return;
    }

    cartContainer.innerHTML = "";
    cart.forEach((product, index) => {
        let productDiv = document.createElement("div");
        productDiv.innerHTML = `
            <p>${product.name} - ₹${product.price} x ${product.quantity}
            <button onclick="increaseQuantity(${index})">+</button>
            <button onclick="decreaseQuantity(${index})">-</button>
            <button onclick="removeFromCart(${index})">Remove</button>
            </p>`;
        cartContainer.appendChild(productDiv);
    });

    updateCartCount();
}

// Function to update cart count in UI
function updateCartCount() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById("cart-count").textContent = cartCount;
}

// Function to remove an item from the cart
function removeFromCart(index) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart.splice(index, 1);
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCart();
}

// Function to increase product quantity in the cart
function increaseQuantity(index) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart[index].quantity += 1;
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCart();
}

// Function to decrease product quantity in the cart
function decreaseQuantity(index) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    if (cart[index].quantity > 1) {
        cart[index].quantity -= 1;
    } else {
        cart.splice(index, 1); // Remove item if quantity is 1
    }
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCart();
}

// Function to clear the entire cart
function clearCart() {
    localStorage.removeItem("cart");
    loadCart();
}

// Load cart count when the page loads
document.addEventListener("DOMContentLoaded", function () {
    updateCartCount();
    if (document.getElementById("cartContainer")) {
        loadCart();
    }
});

// LOGOUT
function logout() {
    fetch('/logout', { method: 'POST' })
        .then(response => {
            if (response.ok) {
                window.location.href = '/';
            } else {
                alert('Logout failed!');
            }
        })
        .catch(error => console.error('Error:', error));
}


//ACCOUNT
document.getElementById("account-form").addEventListener("submit", function(event) {
    event.preventDefault();

    let formData = new FormData(this);
    
    fetch("/account", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error("Error:", error);
    });
});