from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileUpdateForm, UserLoginForm, UserRegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.first_name or user.username}! Ro‘yxatdan muvaffaqiyatli o‘tdingiz.")
            if user.is_business:
                return redirect('b2b:dashboard')
            return redirect('core:home')
        else:
            messages.error(request, "Ro‘yxatdan o‘tishda xatolik yuz berdi. Iltimos, ma’lumotlarni tekshiring.")
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Salom, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_business:
                return redirect('b2b:dashboard')
            return redirect('core:home')
        else:
            messages.error(request, "Login yoki parol noto‘g‘ri kiritildi.")
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('core:home')


@login_required
def profile_view(request):
    from apps.bookings.models import Booking
    from apps.payments.models import QuietPass, Payment
    from apps.gamification.models import RewardTransaction
    from apps.reviews.models import Review
    from apps.measurements.models import InternetTest

    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil ma’lumotlari muvaffaqiyatli saqlandi.")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=user)

    recent_bookings = Booking.objects.filter(user=user).select_related('location', 'table', 'table__zone')[:5]
    active_pass = QuietPass.objects.filter(user=user, status='active').first()
    reward_history = RewardTransaction.objects.filter(user=user).order_by('-created_at')[:10]
    my_reviews = Review.objects.filter(user=user).select_related('location')[:5]
    my_tests = InternetTest.objects.filter(user=user).select_related('location')[:5]

    context = {
        'form': form,
        'recent_bookings': recent_bookings,
        'active_pass': active_pass,
        'reward_history': reward_history,
        'my_reviews': my_reviews,
        'my_tests': my_tests,
    }
    return render(request, 'accounts/profile.html', context)
