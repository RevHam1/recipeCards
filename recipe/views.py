from django.shortcuts import render, redirect
from .models import * 
from django.contrib import messages
import bcrypt
import requests
from django.conf import settings

## Register & Login
def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        errors = User.objects.reg_validator(request.POST)
        if errors:
            for value in errors.values():
                messages.error(request, value)
            return redirect('/')

        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            password = hashed_pw
        )
        request.session['user_id'] = user.id
        return redirect('/recipe')
    return redirect('/')

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST['email'])
        if user:
            user = user[0]      
            if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
                request.session['user_id'] = user.id
                return redirect('/recipe')
        messages.error(request, "Email or password is incorrect")
    return redirect('/')
    

def recipe(request):
    if 'user_id' not in request.session:
        return redirect('/')

    recipes = []
    if request.method == 'POST':
        search_url = 'https://api.spoonacular.com/recipes/random' 

        params = {
            'tags' : request.POST['search'],
            'apiKey': settings.SPOONACULAR_API_KEY,
            'number' : 1,
        }

        r = requests.get(search_url, params=params)

        results = r.json()["recipes"]

        # recipes = []
        for result in results:
            recipe_data = {
                'id':result["id"],
                'title':result["title"],
                'ready':result["readyInMinutes"],
                'servings':result["servings"],
                'image':result["image"],
                'summary':result["summary"],
                'instructions':result["instructions"],
            }

            recipes.append(recipe_data)
       
    context = {
        'current_user': User.objects.get(id=request.session['user_id']),
        'recipes': recipes,
    }
    return render(request, "recipe.html", context)

def logout(request):
    request.session.flush()
    # request.session.clear()
    return redirect('/')

def save(request):
    if 'user_id' not in request.session:
        return redirect('/')

    user = User.objects.get(id=request.session['user_id'])
    card = Card.objects.create(
        title = request.POST['title'],
        image_url = request.POST['image'],
        summary = request.POST['summary'],
        instructions = request.POST['instructions'],
        ready = request.POST['ready'],
        servings = request.POST['servings'],
        cook = user
    )

    return redirect('/recipes_saved')

def recipes_saved(request):
    context = {
        'current_user': User.objects.get(id=request.session['user_id']),
        'all_cards': Card.objects.all,
    }    
    return render(request, 'recipes_saved.html', context)

def delete(request, card_id):
    if request.method == "GET":
        context = {
            "card": Card.objects.get(id=card_id)
        }
        return render(request,'delete.html', context)

    if request.method == "POST":
        card = Card.objects.get(id=card_id)
        card.delete()
        return redirect("/recipes_saved")


