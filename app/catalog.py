"""Local, transparent demonstration catalog. Prices are illustrative, not live quotes."""
from __future__ import annotations

PRODUCTS = {
    'chickpeas': {'name': 'Chickpeas', 'unit': 'can', 'price': 1.45, 'icon': '🫘'},
    'tomatoes': {'name': 'Crushed tomatoes', 'unit': 'can', 'price': 1.85, 'icon': '🍅'},
    'coconut_milk': {'name': 'Coconut milk', 'unit': 'can', 'price': 2.65, 'icon': '🥥'},
    'rice': {'name': 'Rice', 'unit': 'bag', 'price': 3.25, 'icon': '🍚'},
    'spinach': {'name': 'Spinach', 'unit': 'bag', 'price': 2.25, 'icon': '🥬'},
    'pasta': {'name': 'Pasta', 'unit': 'box', 'price': 2.50, 'icon': '🍝'},
    'pesto': {'name': 'Basil pesto', 'unit': 'jar', 'price': 3.60, 'icon': '🌿'},
    'cherry_tomatoes': {'name': 'Cherry tomatoes', 'unit': 'box', 'price': 3.20, 'icon': '🍅'},
    'tortillas': {'name': 'Tortillas', 'unit': 'pack', 'price': 3.00, 'icon': '🌮'},
    'black_beans': {'name': 'Black beans', 'unit': 'can', 'price': 1.90, 'icon': '🫘'},
    'bell_peppers': {'name': 'Bell peppers', 'unit': 'piece', 'price': 1.30, 'icon': '🫑'},
    'cheese': {'name': 'Cheddar cheese', 'unit': 'bag', 'price': 3.55, 'icon': '🧀'},
    'salsa': {'name': 'Salsa', 'unit': 'jar', 'price': 2.75, 'icon': '🥫'},
    'potatoes': {'name': 'Potatoes', 'unit': 'bag', 'price': 4.50, 'icon': '🥔'},
    'eggs': {'name': 'Eggs', 'unit': 'carton', 'price': 3.50, 'icon': '🥚'},
    'onions': {'name': 'Onions', 'unit': 'bag', 'price': 2.10, 'icon': '🧅'},
    'flour': {'name': 'Flour', 'unit': 'bag', 'price': 2.60, 'icon': '🌾'},
    'milk': {'name': 'Milk', 'unit': 'carton', 'price': 2.90, 'icon': '🥛'},
}

RECIPES = [
    {'id': 'chickpea-curry', 'name': 'Coconut chickpea curry', 'tag': 'Comfort food', 'emoji': '🍛', 'minutes': 30, 'vegetarian': True,
     'ingredients': {'chickpeas': 2, 'tomatoes': 1, 'coconut_milk': 1, 'rice': 1, 'spinach': 1},
     'steps': ['Rinse and cook the rice.', 'Simmer chickpeas, tomatoes and coconut milk.', 'Fold in spinach; serve the curry over rice.']},
    {'id': 'pesto-pasta', 'name': 'Garden pesto pasta', 'tag': 'Quick & easy', 'emoji': '🍝', 'minutes': 20, 'vegetarian': True,
     'ingredients': {'pasta': 2, 'pesto': 1, 'cherry_tomatoes': 1, 'spinach': 1},
     'steps': ['Boil pasta until al dente.', 'Warm cherry tomatoes and spinach.', 'Toss everything with pesto.']},
    {'id': 'veggie-tacos', 'name': 'Colorful veggie tacos', 'tag': 'Family favorite', 'emoji': '🌮', 'minutes': 25, 'vegetarian': True,
     'ingredients': {'tortillas': 1, 'black_beans': 2, 'bell_peppers': 2, 'cheese': 1, 'salsa': 1},
     'steps': ['Warm the black beans with seasoning.', 'Sauté sliced bell peppers.', 'Fill tortillas; serve with cheese and salsa.']},
    {'id': 'breakfast-dinner', 'name': 'Golden potato & egg skillet', 'tag': 'Budget smart', 'emoji': '🍳', 'minutes': 25, 'vegetarian': True,
     'ingredients': {'eggs': 1, 'potatoes': 1, 'onions': 1, 'spinach': 1},
     'steps': ['Dice and pan-roast potatoes until tender.', 'Add onions and wilt the spinach.', 'Crack eggs over the vegetables; cook through.']},
    {'id': 'tomato-pasta', 'name': 'Cozy tomato pasta', 'tag': 'Pantry rescue', 'emoji': '🍅', 'minutes': 20, 'vegetarian': True,
     'ingredients': {'pasta': 2, 'tomatoes': 2, 'onions': 1, 'cheese': 1},
     'steps': ['Cook the pasta in salted water.', 'Simmer tomatoes and onion into a rich sauce.', 'Toss together and finish with cheese.']},
]

DEFAULT_PANTRY = {'chickpeas': 1, 'tomatoes': 1, 'rice': 1, 'spinach': 1, 'pasta': 1, 'tortillas': 1, 'eggs': 1, 'onions': 1}
MEMBERS = ['Alex', 'Sam']
