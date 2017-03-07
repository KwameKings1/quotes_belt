from django.shortcuts import render, redirect
from .models import *
import bcrypt
from django.contrib import messages
from django.db.models import Count

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def create_user(request):
    check = User.objects.validate_user(request.POST)
    if check == True:
        user = User.objects.create(
            name = request.POST.get('name'),
            alias = request.POST.get('alias'),
            email = request.POST.get('email'),
            password = bcrypt.hashpw(request.POST.get('password').encode(), bcrypt.gensalt()),
            date_of_birth = request.POST.get('dob'),
        )
        request.session['user_id'] = user.id
        return redirect('/quotes')
    else:
        for message in check:
            messages.error(request, message)
        return redirect('/')

def login_user(request):
    login = User.objects.login_user(request.POST)
    if login[0]:
        request.session['user_id'] = login[1].id
        return redirect('/quotes')
    else:
        messages.error(request, login[1])
        return redirect('/')
    return redirect('/quotes')

def main_page(request):
    current_user = User.objects.get(id = request.session['user_id'])
    favs = current_user.favorites.all()
    quote_ids = []
    for fav in favs:
        quote_ids.append(fav.quote.id)
    quotes = Quote.objects.exclude(id__in=quote_ids)
    context = {
        'current_user': current_user,
        'favs': favs,
        'quotes': quotes,
    }
    return render(request, 'main/quotes.html', context)

def add_quote(request):
    check_two = Quote.objects.validate_quote(request.POST)
    if check_two == True:
        quote = Quote.objects.create(
            quoted_by = request.POST.get('quoted_by'),
            message = request.POST.get('message'),
            user = User.objects.get(id = request.session['user_id'])
        )
        request.session['quote_id'] = quote.id
        return redirect('/quotes')
    else:
        for message in check_two:
            messages.error(request, message)
        return redirect('/quotes')

def user_page(request, id):
    user = User.objects.annotate(num_quotes = Count('quotes')).get(id = id)
    context = {
        'user': user,
        'quotes': user.quotes.all()
    }
    return render(request, 'main/user_page.html', context)

def add_favorite(request, id):
    Favorite.objects.create(
        quote = Quote.objects.get(id = id),
        user = User.objects.get(id = request.session['user_id'])
    )
    return redirect('/quotes')

def destroy_favorite(request, id):
    #delete the Favorite from the DB
    Favorite.objects.get(id = id).delete()
    return redirect('/quotes')

def logout_user(request):
    request.session.clear()
    return redirect('/')
