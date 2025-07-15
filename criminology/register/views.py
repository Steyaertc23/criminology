from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


class CustomLoginView(LoginView):
    redirect_authenticated_user = True

    def get_redirect_url(self):
        return self.request.GET.get("next") or reverse("check_first_login")


class ProtectedLogoutView(LoginRequiredMixin, LogoutView):
    login_url = "/auth/login/"  # or whatever your login URL is

    def handle_no_permission(self):
        return redirect("index")
