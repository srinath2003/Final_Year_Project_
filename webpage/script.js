// Toggle between login and signup forms
function toggleLoginSignup() {
    const modal = document.getElementById('login-signup-form');
    const formTitle = document.getElementById('form-title');
    if (modal.style.display === "flex") {
        modal.style.display = "none";
    } else {
        modal.style.display = "flex";
        // If you want to toggle between login/signup
        formTitle.textContent = "Sign Up";  // Or "Login" based on logic
    }
}

// Basic search functionality (case-insensitive)
document.getElementById('search').addEventListener('input', function (e) {
    const query = e.target.value.toLowerCase();
    const products = document.querySelectorAll('.product-card');
    
    products.forEach(function (product) {
        const productName = product.querySelector('h3').textContent.toLowerCase();
        if (productName.includes(query)) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
});


function viewProductDetails(productId) {
    console.log("Product ID:", productId); // Debugging
    window.location.href = `/product/${productId}`;
}
