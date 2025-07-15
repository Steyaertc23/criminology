"""
@file criminals/views.py
@brief Views for managing and displaying Criminal records and their offenses.

@details
Provides views for:
- Homepage and authenticated dashboard
- Viewing all or filtered criminals
- Offense prioritization
- Adding criminals via form or CSV upload
- Search functionality
- Admin-only actions
"""

import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.db import transaction
from .forms import CriminalForm, CriminalOffenseForm
from .models import Criminal, FederalOffense, VACodeOffense, CriminalOffenseLink

# ───────────────────────────────────────────────
# Authentication & Access Control
# ───────────────────────────────────────────────


def is_admin(user):
    """
    @brief Checks if the user has admin privileges.

    @param user Django User instance.
    @return True if the user is staff (admin), otherwise False.
    """
    return user.is_staff


# ───────────────────────────────────────────────
# Homepage & Navigation
# ───────────────────────────────────────────────


def index(request):
    """
    @brief Public landing page.

    @details
    Redirects to home page if the user is authenticated, otherwise renders 'index.html'.
    """
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "index.html")


@login_required
def home(request):
    """
    @brief Authenticated user's dashboard.

    @return Rendered template for user home.
    """
    return render(request, "criminals/home.html")


# ───────────────────────────────────────────────
# Offense Prioritization
# ───────────────────────────────────────────────

OFFENSE_PRIORITY = {
    "Felony": 3,
    "Misdemeanor": 2,
    "Infraction": 1,
}


def get_highest_offense(criminal):
    """
    @brief Determines the highest-priority offense for a criminal.

    @param criminal Criminal instance.
    @return Tuple of (score: int, source: str, offense: FederalOffense or VACodeOffense)
    """
    links = criminal.offense_links.all()
    max_score = 0
    max_source = None
    max_offense = None

    for link in links:
        offense = link.federal_offense or link.vacode_offense
        if not offense:
            continue
        score = OFFENSE_PRIORITY.get(offense.offense_type, 0)
        if score > max_score:
            max_score = score
            max_offense = offense
            max_source = offense.source

    return max_score, max_source, max_offense


# ───────────────────────────────────────────────
# View Criminals
# ───────────────────────────────────────────────


def get_criminals_with_offenses():
    """
    @brief Fetches all criminals with their related offense links.

    @return QuerySet of Criminals with prefetch_related CriminalOffenseLinks and offenses.
    """
    return Criminal.objects.prefetch_related(
        Prefetch(
            "offense_links",
            queryset=CriminalOffenseLink.objects.select_related(
                "federal_offense", "vacode_offense"
            ),
        )
    )


@login_required
def view_all_criminals(request):
    """
    @brief View of all criminals grouped by offense type and source.

    @details
    Groups and paginates criminals by:
    - Federal Felons
    - Federal Misdemeanors
    - Federal Infractions
    - Virginia Felons
    - Virginia Misdemeanors
    - Virginia Infractions
    """
    categorized = {
        "Federal Felons": [],
        "Federal Misdemeanors": [],
        "Federal Infractions": [],
        "Virginia Felons": [],
        "Virginia Misdemeanors": [],
        "Virginia Infractions": [],
    }

    criminals = get_criminals_with_offenses()

    for criminal in criminals:
        score, source, offense = get_highest_offense(criminal)
        if not offense:
            continue

        key = f"{source.capitalize()} {offense.offense_type}s"
        criminal.highest_offense = offense
        categorized[key].append(criminal)

    paginated_sections = []
    get_params = request.GET.copy()

    for label, criminals_list in categorized.items():
        paginator = Paginator(criminals_list, 10)
        page_key = f'page_{label.replace(" ", "_").lower()}'
        page_number = request.GET.get(page_key, 1)
        page_obj = paginator.get_page(page_number)
        params = get_params.copy()
        params.pop(page_key, None)

        paginated_sections.append(
            {
                "label": label,
                "page_obj": page_obj,
                "page_key": page_key,
                "params": params.urlencode(),
            }
        )

    return render(
        request,
        "criminals/all_criminals.html",
        {"criminal_sections": paginated_sections},
    )


def paginate_classified_criminals(request, class_categories, class_labels):
    """
    @brief Helper to paginate classified criminals (by offense class).

    @param request Django request.
    @param class_categories Dict[class -> List[Criminal]]
    @param class_labels Dict[class -> str]
    @return List of paginated section dictionaries.
    """
    paginated_sections = []
    get_params = request.GET.copy()

    for cls, criminals in class_categories.items():
        if criminals:
            paginator = Paginator(criminals, 10)
            page_key = f"page_{cls.lower() if cls else 'unknown'}"
            page_number = request.GET.get(page_key, 1)
            page_obj = paginator.get_page(page_number)
            label = class_labels.get(cls, cls)
            params = get_params.copy()
            params.pop(page_key, None)

            paginated_sections.append(
                {
                    "label": label,
                    "page_obj": page_obj,
                    "page_key": page_key,
                    "params": params.urlencode(),
                }
            )

    return paginated_sections


def filter_and_render_by_class(request, offense_cls, label, score, source_key):
    """
    @brief Filters criminals by offense class and renders the view.

    @param offense_cls Offense model class (FederalOffense or VACodeOffense).
    @param label Template suffix to use.
    @param score Offense score (1, 2, or 3).
    @param source_key 'federal' or 'virginia'.
    @return Rendered response with paginated sections.
    """
    class_categories = {cls: [] for cls, _ in offense_cls.CLASS_CHOICES}
    criminals = get_criminals_with_offenses()

    for criminal in criminals:
        score_val, source, offense = get_highest_offense(criminal)
        if score_val == score and source == source_key and offense:
            criminal.highest_offense = offense
            cls_val = getattr(offense, "offense_class", None)
            class_categories.setdefault(cls_val, []).append(criminal)

    labels = dict(offense_cls.CLASS_CHOICES)
    if None in class_categories:
        labels[None] = "Unknown Class"

    sections = paginate_classified_criminals(request, class_categories, labels)
    return render(
        request, f"criminals/view_{label}.html", {"criminal_sections": sections}
    )


@login_required
def view_federal_felons(request):
    """@brief View of all federal felons."""
    return filter_and_render_by_class(
        request, FederalOffense, "federal_felons", 3, "federal"
    )


@login_required
def view_federal_misdemeanors(request):
    """@brief View of all federal misdemeanors."""
    return filter_and_render_by_class(
        request, FederalOffense, "federal_misdemeanors", 2, "federal"
    )


@login_required
def view_federal_infractions(request):
    """@brief View of all federal infractions."""
    return filter_and_render_by_class(
        request, FederalOffense, "federal_infractions", 1, "federal"
    )


@login_required
def view_state_felons(request):
    """@brief View of all state (Virginia) felons."""
    return filter_and_render_by_class(
        request, VACodeOffense, "state_felons", 3, "virginia"
    )


@login_required
def view_state_misdemeanors(request):
    """@brief View of all state (Virginia) misdemeanors."""
    return filter_and_render_by_class(
        request, VACodeOffense, "state_misdemeanors", 2, "virginia"
    )


@login_required
def view_state_infractions(request):
    """@brief View of all state (Virginia) infractions."""
    return filter_and_render_by_class(
        request, VACodeOffense, "state_infractions", 1, "virginia"
    )


@login_required
def search_results(request, name: str):
    """
    @brief Performs name-based search for criminals.

    @param name Query string to search first or last name.
    @return Rendered search results page.
    """
    query = name.strip().lower()
    criminals = Criminal.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query)
    )
    return render(
        request, "criminals/search.html", {"criminals": criminals, "query": name}
    )


# ───────────────────────────────────────────────
# Criminal Creation
# ───────────────────────────────────────────────


@login_required
def add_criminal(request):
    """
    @brief Adds a new criminal and offense through a form.

    @details
    If the form is valid, creates a Criminal and links it to a federal or state offense.

    @return Redirects to 'home' on success; re-renders form on failure.
    """
    if request.method == "POST":
        criminal_form = CriminalForm(request.POST)
        offense_form = CriminalOffenseForm(request.POST)

        if criminal_form.is_valid() and offense_form.is_valid():
            criminal = criminal_form.save()
            data = offense_form.cleaned_data
            offense_model = (
                FederalOffense if data["offense_source"] == "federal" else VACodeOffense
            )

            offense_obj, _ = offense_model.objects.get_or_create(
                offense_type=data["offense_type"],
                offense_class=data["offense_class"],
                description=data["description"],
            )

            CriminalOffenseLink.objects.create(
                criminal=criminal,
                federal_offense=(
                    offense_obj if isinstance(offense_obj, FederalOffense) else None
                ),
                vacode_offense=(
                    offense_obj if isinstance(offense_obj, VACodeOffense) else None
                ),
            )

            messages.success(request, "Criminal successfully added.")
            return redirect("home")
        else:
            messages.error(request, "There were errors in the form.")
    else:
        criminal_form = CriminalForm()
        offense_form = CriminalOffenseForm()

    return render(
        request,
        "criminals/add_criminal.html",
        {"criminal_form": criminal_form, "offense_form": offense_form},
    )


@login_required
@user_passes_test(is_admin)
def mass_add_criminals(request):
    """
    @brief Bulk adds criminals and offenses from a CSV file.

    @details
    Validates headers and processes rows. Rolls back on failure.
    CSV format: first_name,last_name,offense_type,offense_class,description,offense_source

    @return Redirects with success or error messages.
    """
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a valid .csv file.")
            return redirect("mass_add_criminals")

        try:
            decoded = csv_file.read().decode("utf-8")
            reader = csv.reader(io.StringIO(decoded))

            expected_header = [
                "first_name",
                "last_name",
                "offense_type",
                "offense_class",
                "description",
                "offense_source",
            ]
            header = next(reader, None)
            if not header or [h.strip().lower() for h in header] != expected_header:
                messages.error(
                    request,
                    f"Invalid CSV header. Expected: {','.join(expected_header)}",
                )
                return redirect("mass_add_criminals")

            count = 0
            with transaction.atomic():
                current_criminal = None
                current_name = None

                for row_num, row in enumerate(reader, start=2):
                    if len(row) != 6:
                        messages.warning(
                            request, f"Skipping row {row_num}: wrong number of fields."
                        )
                        continue

                    fn, ln, otype, oclass, desc, src = [r.strip() for r in row]
                    row_name = (fn.lower(), ln.lower())

                    if current_name != row_name:
                        current_criminal = Criminal.objects.create(
                            first_name=fn, last_name=ln
                        )
                        current_name = row_name

                    offense_model = (
                        FederalOffense if src.lower() == "federal" else VACodeOffense
                    )
                    offense_obj, _ = offense_model.objects.get_or_create(
                        offense_type=otype,
                        offense_class=oclass,
                        description=desc,
                    )

                    CriminalOffenseLink.objects.create(
                        criminal=current_criminal,
                        federal_offense=(
                            offense_obj
                            if isinstance(offense_obj, FederalOffense)
                            else None
                        ),
                        vacode_offense=(
                            offense_obj
                            if isinstance(offense_obj, VACodeOffense)
                            else None
                        ),
                    )

                    count += 1

            messages.success(request, f"Successfully added {count} offense records.")
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
        return redirect("mass_add")

    return render(request, "criminals/mass_add_criminals.html")
