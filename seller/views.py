from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, SellerProfile
from .forms import ProductForm
from django.contrib.auth.hashers import make_password
from django.db import transaction
from core.models import User  

#registration
def seller_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        store_name = request.POST.get("store_name")
        store_description = request.POST.get("store_description")

     
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("seller_register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("seller_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("seller_register")

       
        with transaction.atomic():
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                role="SELLER",      # Assign seller role
            )

            SellerProfile.objects.create(
                user=user,
                store_name=store_name,
                store_description=store_description
            )

        messages.success(request, "Seller account created successfully! Please login.")
        return redirect("seller_login")

    return render(request, "seller/register.html")


#login
def seller_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        #login only if seller profile exists
        if user is not None and hasattr(user, 'seller_profile'):
            login(request, user)
            return redirect('seller_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a seller account.")

    return render(request, "seller/login.html")


def seller_logout(request):
    logout(request)
    return redirect('seller_login')


# Dashboard
@login_required
def seller_dashboard(request):
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, "Access denied.")
        return redirect('seller_login')

    seller = request.user.seller_profile
    product_count = seller.products.count()

    return render(request, "seller/dashboard.html", {
        "seller": seller,
        "product_count": product_count,
    })


# ------------------------------------
# Product List
# ------------------------------------
@login_required
def product_list(request):
    seller = request.user.seller_profile
    products = seller.products.all()

    return render(request, "seller/product_list.html", {
        "products": products,
    })


# ------------------------------------
# Add Product
# ------------------------------------
@login_required
def product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller_profile
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('product_list')

    else:
        form = ProductForm()

    return render(request, "seller/product_form.html", {
        "form": form,
        "title": "Add Product",
    })


# ------------------------------------
# Edit Product
# ------------------------------------
@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user.seller_profile)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('product_list')

    else:
        form = ProductForm(instance=product)

    return render(request, "seller/product_form.html", {
        "form": form,
        "title": "Edit Product",
    })


# ------------------------------------
# Delete Product
# ------------------------------------
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user.seller_profile)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('product_list')

    return render(request, "seller/product_confirm_delete.html", {
        "product": product
    })
