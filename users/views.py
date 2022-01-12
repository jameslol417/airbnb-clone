import os
import requests

# from django.views import View
from django.views.generic import FormView  # generic login use import, use CCBV
from django.urls import reverse_lazy  # simpler reverse
from django.shortcuts import redirect, reverse  # added for login / +render for manual
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile

# from django.contrib.auth.forms import UserCreationForm
from . import forms, models


# class LoginView(View):
#     def get(self, request):
#         form = forms.LoginForm(initial={"email": "jtex417@naver.com"})
#         return render(request, "users/login.html", {"form": form})

#     def post(self, request):
#         form = forms.LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get("email")
#             password = form.cleaned_data.get("password")
#             user = authenticate(request, username=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect(reverse("core:home"))
#         return render(request, "users/login.html", {"form": form})
# ------------------------manual---------------------------


class LoginView(FormView):
    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(self.request, username=email, password=password)
            if user is not None:
                login(self.request, user)
        return super().form_valid(form)


def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(FormView):

    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    # form_class = UserCreationForm
    success_url = reverse_lazy("core:home")
    # initial = {
    #     "first_name": "Elon",
    #     "last_name": "Muskette",
    #     "email": "henrylol4177@gmail.com",
    # }

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # to do add success messsage
    except models.User.DoesNotExist:
        # to do add error messsage
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user,user:email"
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        code = request.GET.get("code", None)
        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException()
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                email_request = requests.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                email_json = email_request.json()
                print(email_json)
                # print(profile_json) > debugging received github profile data
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    if email is None:
                        email = email_json[0].get("email")
                    bio = profile_json.get("bio")
                    try:
                        user = models.User.objects.get(email=email)
                        # verifying existing user
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException()
                    except models.User.DoesNotExist:
                        name = username if name is None else name
                        email = username if email is None else email
                        bio = "" if bio is None else bio
                        user = models.User.objects.create(
                            email=email,
                            username=email,
                            first_name=name,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException()
        else:
            raise GithubException()
    except GithubException:
        # send error message
        return redirect(reverse("users:login"))


def kakao_login(request):
    client_id = os.environ.get("KAKAO_ID")
    REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={REDIRECT_URI}&response_type=code&scope=account_email"
    )


class KakaoException(Exception):
    # to do logout kakao user
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code")
        client_id = os.environ.get("KAKAO_ID")
        REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={REDIRECT_URI}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException()
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()
        print(profile_json)
        email = profile_json.get("kakao_account").get("email")
        try:
            properties = profile_json.get("properties")
            nickname = properties.get("nickname")
            profile_image = (
                profile_json.get("kakao_account")
                .get("profile")
                .get("profile_image_url")
            )
        except:
            nickname = email
            profile_image = None
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                # add message showing which login method was used to create account
                raise KakaoException()
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(photo_request.content)
                )
        login(request, user)
        return redirect(reverse("core:home"))
    except KakaoException:
        return redirect(reverse("users:login"))
