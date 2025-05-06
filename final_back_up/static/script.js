

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

// Search Bar Functionality (Button Click Only) ## Srinath - Altered
if (document.getElementById('searchBar')) {
    document.getElementById('searchButton').addEventListener('click', function() {
        let searchQuery = document.getElementById('searchBar').value.trim().toLowerCase();
        if (searchQuery === '') {
            return; // Don't run the search if input is empty
        }
        let filteredProducts = allProducts.filter(product => {
            return product.Name.toLowerCase().includes(searchQuery) ||
                   product.Category.toLowerCase().includes(searchQuery) ||
                   product.Brand.toLowerCase().includes(searchQuery);
        });
    
        displayProducts(filteredProducts);
    });
}
//Search bar with the enter key ## Srinath
document.getElementById('searchBar').addEventListener('keyup', function(e) {
    if (e.key === 'Enter') {
        document.getElementById('searchButton').click();
    }
});



// Call this to initialize
function populateFilters(products) {
    allProducts = products; // Save products globally

    let categorySet = new Set();
    products.forEach(product => categorySet.add(product.Category));

    let categoryDropdown = document.getElementById('categoryFilter');
    categorySet.forEach(category => {
        let option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryDropdown.appendChild(option);
    });

    // Initial brand filter population
    categoryDropdown.addEventListener('change', function () {
        updateBrandCheckboxes(this.value);
        selectedBrands.clear(); // Clear previous selection
    });

    // Optional: populate brands on initial load (e.g., show all brands)
    updateBrandCheckboxes(null);
}

function updateBrandCheckboxes(selectedCategory) {
    let brandDropdown = document.getElementById('brandFilter');
    brandDropdown.innerHTML = ''; // Clear previous checkboxes

    let filteredProducts = selectedCategory
        ? allProducts.filter(p => p.Category === selectedCategory)
        : allProducts;

    let brandSet = new Set();
    filteredProducts.forEach(product => brandSet.add(product.Brand));

    brandSet.forEach(brand => {
        let label = document.createElement('label');
        label.innerHTML = `<input value="${brand}" type="checkbox"> ${brand}`;
        brandDropdown.appendChild(label);

        // Add event listener to each checkbox
        label.querySelector('input').addEventListener('change', function () {
            if (this.checked) {
                selectedBrands.add(brand);
            } else {
                selectedBrands.delete(brand);
            }
             // Re-filter products
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
    if (document.getElementById('productContainer')) {
        let container = document.getElementById('productContainer');
        container.innerHTML = '';
    
        products.forEach(product => {
            let productCard = document.createElement('div');
            productCard.classList.add('product-card');
    
            productCard.innerHTML = `
                <img src="${product.Image}" alt="${product.Name}">
                <div class="card-content">
                <h2 class="product-card-h2">${product.Name}</h2>
                <p class="product-card-p"><strong>Category:</strong> ${product.Category}</p>
                <p class="product-card-p"><strong>Brand:</strong> ${product.Brand}</p>
                <p class="product-card-p"><strong>Price:</strong> ₹${product.Price}</p>
                <p class="product-card-p"><strong>Stock Left:</strong> ${product.Stock_Quantity}</p>
                <p class="product-card-p"><strong>Rating:</strong> ⭐${product.Rating} (${product.Rating_Count} reviews)</p>
                <div class="product-buttons">
                     <a href="/product/${product.ID}" class="view-details" onclick="logAndNavigate(event, '${product.ID}', '${product.Category}', this)">View Details</a>
                    <button class="add-to-cart" onclick="logInteraction('${product.ID}', 'add_to_cart', this, '${product.Category}');addToCart(${product.ID}, '${product.Name}', ${product.Price}, '${product.Image}', ${product.Rating})">Add to Cart</button>
                    <button class="like" onclick="logInteraction('${product.ID}', 'like', this, '${product.Category}');addToWishList(${product.ID}, '${product.Name}', '${product.Category}', '${product.Brand}', ${product.Stock_Quantity}, ${product.Price}, '${product.Image}', ${product.Rating})">❤️ Like</button>
                </div>
                </div>
            `;
    
            container.appendChild(productCard);
        });   
    }
}
//## Srinath
//log and view details
function logAndNavigate(event, productId, category, element) {
    event.preventDefault(); // Prevent immediate navigation

    logInteraction(productId, 'view_details', element, category);

    // Delay navigation slightly to ensure the log request is sent
    setTimeout(() => {
        window.location.href = element.href;
    }, 300); // Adjust the delay as needed
}
//## Srinath
// Log interaction (click events)
function logInteraction(productId, action, button, category = "Unknown") {
    

    fetch('/log_interaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            product_id: productId,
            //user_id: userId,
            //session_id: sessionId,
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
// searchText Logging - srinath
document.getElementById('searchButton').addEventListener('click', () => {
    const searchText = document.getElementById('searchBar').value.trim();
    console.log('Search Text:', searchText);
     // Only log if the search text is not empty
     if (searchText !== '') {
        logsearchInteraction('search', searchText);
    }
});

function logFullFilterInteraction(filterData) {
    fetch('/log_filter_interaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(filterData)
    }).then(response => {
        if (!response.ok) {
            console.error('Failed to log full filter interaction');
        }
    }).catch(err => {
        console.error('Error logging filter interaction:', err);
    });
}


document.getElementById('categoryFilter').addEventListener('change', (e) => {
    const selectedCategory = e.target.value;
   // logFilterInteraction('filter_category', selectedCategory, selectedCategory);
});

document.getElementById('brandFilter').addEventListener('change', (e) => {
    if (e.target && e.target.type === 'checkbox') {
        const selectedBrand = e.target.value;
        //logFilterInteraction('filter_brand', selectedBrand, selectedBrand);
    }
});

document.querySelector('.applybtn').addEventListener('click', () => {
    const selectedCategory = document.getElementById('categoryFilter').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    const rating = document.getElementById('rating').value;
    const selectedBrandsArray = Array.from(selectedBrands);

    const fullFilterPayload = {
        action: 'apply_filters',
        category: selectedCategory || 'All',
        brands: selectedBrandsArray,
        min_price: minPrice || null,
        max_price: maxPrice || null,
        rating: rating || null,
        action_timestamp: new Date().toISOString()
    };
    // ✅ Log all filters in one go
    logFullFilterInteraction(fullFilterPayload);
    //const filterDetails = `minPrice=${minPrice}, maxPrice=${maxPrice}, rating=${rating}`;
    //logFilterInteraction('apply_filters', filterDetails);
    applyFilters();
});
//## Srinath
// log filter Interactions
function logsearchInteraction(actionType, value = "", category = "filter") {
    let sessionId = sessionStorage.getItem("session_id");
    fetch('/log_search_interaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        
        body: JSON.stringify({
            //user_id: userId,
            session_id: sessionId,
            action: actionType,         // e.g., 'search', 'filter_category', etc.
            value: value,               // e.g., 'shoes', 'Electronics', 'Nike', etc.
            action_timestamp: new Date().toISOString()
        })
    });
}

  
// CART FUNCTIONALITY
function addToCart(id, name, price, image, rating) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    // Check if the product already exists in the cart
    let existingProduct = cart.find(item => item.id === id);
    if (existingProduct) {
        existingProduct.quantity += 1; // Increase quantity
    } else {
        cart.push({ id, name, price, quantity: 1, image, rating }); // Add new product
    }

    localStorage.setItem("cart", JSON.stringify(cart));
    updateCartCount();
}

// Function to load cart items in cart.html
function loadCart() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartContainer = document.getElementById("cartContainer");
    let cartTotalContainer = document.getElementById("cartTotalContainer");

    // Clear previous content in both containers
    cartContainer.innerHTML = "";
    cartTotalContainer.innerHTML = "";

    if (cart.length === 0) {
        cartContainer.innerHTML = "<p>Your cart is empty.</p>";
        updateCartCount();
        displayCartTotal(0); // Display 0 total if cart is empty
        return;
    }

    let totalAmount = 0;
    cart.forEach((product, index) => {
        let productDiv = document.createElement("div");
        productDiv.classList.add('cart-card'); // Apply the same card style

        const itemTotal = product.price * product.quantity;
        totalAmount += itemTotal;

        productDiv.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <div class="card-content">
            <h2 class="product-card-h2">${product.name}</h2>
            <p class="product-card-p"><strong>Price:</strong> ₹${product.price}</p>
            <p class="product-card-p"><strong>Quantity:</strong> ${product.quantity}</p>
            <p class="product-card-p"><strong>Total:</strong> ₹${itemTotal}</p>
            <p class="product-card-p"><strong>Rating:</strong> ⭐${product.rating}</p>
            <div class="cart-buttons">
                <button onclick="increaseQuantity(${index})">+</button>
                <button onclick="decreaseQuantity(${index})">-</button>
                <button onclick="removeFromCart(${index})">Remove</button>
            </div>
            </div>
        `;
        cartContainer.appendChild(productDiv);
    });

    updateCartCount();
    displayCartTotal(totalAmount);
}

function displayCartTotal(total) {
    let cartTotalContainer = document.getElementById("cartTotalContainer");
    let totalDiv = document.createElement("div");
    totalDiv.classList.add("cart-total");
    totalDiv.innerHTML = `<h3>Total: ₹${total}</h3>`;
    cartTotalContainer.appendChild(totalDiv);
}

//add to wishlist
function addToWishList(id, name, category, brand, quantity, price, image, rating) {
    let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];

    // Check if the product already exists in the wishlist
    let existingProduct = wishlist.find(item => item.id === id);
    if (existingProduct) {
        
    } else {
        wishlist.push({ id, name, category, brand, quantity, price, image, rating }); // Add new product
    }

    localStorage.setItem("wishlist", JSON.stringify(wishlist));
}

// Function to load wishList items in wishlist.html
function loadWishList() {
    let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];
    let wishlistContainer = document.getElementById("wishlistContainer");

    if (wishlist.length === 0) {
        wishlistContainer.innerHTML = "<p>Your wishlist is empty.</p>";
        return;
    }

    wishlistContainer.innerHTML = "";
    wishlist.forEach((product, index) => {
        let productDiv = document.createElement("div");
        productDiv.classList.add('wishlist-card'); // Apply the same card style

        productDiv.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <div class="card-content">
            <h2 class="product-card-h2">${product.name}</h2>
            <p class="product-card-p"><strong>Category:</strong> ${product.category}</p>
            <p class="product-card-p"><strong>Brand:</strong> ${product.brand}</p>
            <p class="product-card-p"><strong>Price:</strong> ₹${product.price}</p>
            <p class="product-card-p"><strong>Stock Left:</strong> ${product.quantity}</p>    
            <p class="product-card-p"><strong>Rating:</strong> ⭐${product.rating}</p>
            <div class="cart-buttons">
                <button onclick="(function() {
                    addToCart(${product.id}, '${product.name}', ${product.price}, '${product.image}', ${product.rating}, '${product.category}', '${product.brand}');
                    removeFromWishList(${index});
                })();">Add to Cart</button>
                <button onclick="removeFromWishList(${index})">Remove</button>
            </div>
            </div>
        `;

        wishlistContainer.appendChild(productDiv);
    });
}

// Function to remove an item from the wishlist
function removeFromWishList(index) {
    let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];
    wishlist.splice(index, 1);
    localStorage.setItem("wishlist", JSON.stringify(wishlist));
    loadWishList();
}

// Function to update cart count in UI
function updateCartCount() {
    let cartCountElement = document.getElementById("cart-count");
    if (cartCountElement) {
        let cart = JSON.parse(localStorage.getItem("cart")) || [];
        let cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCountElement.textContent = cartCount;
    }
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



// // Load cart count when the page loads
// document.addEventListener("DOMContentLoaded", function () {
//     updateCartCount();
//     if (document.getElementById("cartContainer")) {
//         loadCart();
//     }
// });

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
if (document.getElementById("account-form")) {
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
};


// Function to handle the "Buy Now" action
function buyNow() {
    window.location.href = '/orderdetails'; // Redirect to the order details page
}

// Function to dynamically generate the order details page
function loadOrderDetails() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const container = document.querySelector('.container');
    container.innerHTML = ''; // Clear the initial content

    if (cart.length === 0) {
        container.innerHTML = '<p>Please add items to your cart before proceeding to order details.</p>';
        return;
    }

    // Create order header
    const orderHeader = document.createElement('div');
    orderHeader.classList.add('order-header');
    orderHeader.innerHTML = `
        <div class="order-info">
            <h1 class="order-number">Order #TEMP${Date.now().toString().slice(-6)}</h1>
            <p class="order-date">Placed on: ${new Date().toLocaleDateString()}</p>
            <span class="order-status">Pending</span>
        </div>
        <div class="estimated-delivery">
            <p>Estimated Delivery</p>
            <strong>${new Date(Date.now() + (3 * 24 * 60 * 60 * 1000)).toLocaleDateString()}</strong>
        </div>
    `;
    container.appendChild(orderHeader);

    // Create order details grid
    const orderGrid = document.createElement('div');
    orderGrid.classList.add('order-grid');

    // Left column for product details and shipping info
    const leftColumn = document.createElement('div');
    leftColumn.classList.add('left-column');

    const orderDetails = document.createElement('div');
    orderDetails.classList.add('order-details');
    orderDetails.innerHTML = '<h2 class="section-title">Order Details</h2>';

    let subtotal = 0;
    cart.forEach(item => {
        const productItem = document.createElement('div');
        productItem.classList.add('product-item');
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        productItem.innerHTML = `
            <img src="${item.image}" alt="${item.name}" class="product-image">
            <div class="product-details">
                <h3 class="product-name">${item.name}</h3>
                <br>
                <p class="product-price">₹${item.price}</p>
                <br>
                <p class="product-quantity">Quantity: ${item.quantity}</p>
            </div>
        `;
        orderDetails.appendChild(productItem);
    });
    leftColumn.appendChild(orderDetails);

    const shippingInfo = document.createElement('div');
    shippingInfo.classList.add('shipping-info');
    shippingInfo.innerHTML = `
        <h2 class="section-title">Shipping Information</h2>
        <div class="address-details">
            <p><strong>[User Name - Fetch from local storage or server]</strong></p>
            <p>[Shipping Address Line 1 - Fetch]</p>
            <p>[Shipping Address Line 2 - Fetch]</p>
            <p>[City, State, Zip - Fetch]</p>
            <p>[Country - Fetch]</p>
            <p>Phone: [Phone Number - Fetch]</p>
        </div>
    `;
    leftColumn.appendChild(shippingInfo);
    orderGrid.appendChild(leftColumn);

    // Right column for payment summary
    const rightColumn = document.createElement('div');
    rightColumn.classList.add('right-column');

    const paymentSummary = document.createElement('div');
    paymentSummary.classList.add('payment-summary');
    paymentSummary.innerHTML = '<h2 class="section-title">Payment Summary</h2>';

    const shippingCost = subtotal * 0.05; 
    const taxRate = 0.08; 
    const tax = subtotal * taxRate;
    const total = subtotal + shippingCost + tax;

    paymentSummary.innerHTML += `
        <div class="price-row">
            <span>Subtotal</span>
            <span>₹${subtotal.toFixed(2)}</span>
        </div>
        <div class="price-row">
            <span>Shipping</span>
            <span>₹${shippingCost.toFixed(2)}</span>
        </div>
        <div class="price-row">
            <span>Tax</span>
            <span>₹${tax.toFixed(2)}</span>
        </div>
        <div class="total-row">
            <span>Total</span>
            <span>₹${total.toFixed(2)}</span>
        </div>
        <div class="payment-details">
            <h3 class="section-title">Payment Method</h3>
            <h2 style="color: black"><strong>Cash On Delivery</strong></h2>
        </div>
    `;
    rightColumn.appendChild(paymentSummary);
    orderGrid.appendChild(rightColumn);

    container.appendChild(orderGrid);
}

