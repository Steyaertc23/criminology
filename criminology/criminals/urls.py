"""
@file criminals/urls.py
@brief URL routing for the 'criminals' app.

@details
Maps URL patterns to their corresponding views for:
- Homepage and dashboard
- Viewing categorized and all criminals
- Searching for criminals
- Adding criminals manually or via CSV upload
"""

from django.urls import path
from . import views

urlpatterns = [
    # ───────────────────────────────
    # Public / Home
    # ───────────────────────────────
    path('', views.index, name='index'),                         # Public landing page
    path('home/', views.home, name='home'),                      # Authenticated user dashboard

    # ───────────────────────────────
    # View All Criminals
    # ───────────────────────────────
    path('criminals/', views.view_all_criminals, name='all'),    # Paginated view of all categorized criminals

    # ───────────────────────────────
    # Search
    # ───────────────────────────────
    path('criminals/search/<str:name>/', views.search_results, name='search_criminals'),  # Name-based search

    # ───────────────────────────────
    # Federal Categories
    # ───────────────────────────────
    path('criminals/federal/felons/', views.view_federal_felons, name='federal_felony_crimes'),
    path('criminals/federal/misdemeanors/', views.view_federal_misdemeanors, name='federal_misdemeanor_crimes'),
    path('criminals/federal/infractions/', views.view_federal_infractions, name='federal_infraction_crimes'),

    # ───────────────────────────────
    # Virginia (State) Categories
    # ───────────────────────────────
    path('criminals/state/felons/', views.view_state_felons, name='va_felony_crimes'),
    path('criminals/state/misdemeanors/', views.view_state_misdemeanors, name='va_misdemeanor_crimes'),
    path('criminals/state/infractions/', views.view_state_infractions, name='va_infraction_crimes'),

    # ───────────────────────────────
    # Admin / Create
    # ───────────────────────────────
    path('criminals/add/', views.add_criminal, name='add'),              # Manual single entry
    path('criminals/mass_add/', views.mass_add_criminals, name='mass_add'),  # CSV bulk import
]
