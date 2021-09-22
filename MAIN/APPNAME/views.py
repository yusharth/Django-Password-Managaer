from base64 import encode
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import random
from django.core.mail import send_mail
from cryptography.fernet import Fernet
from mechanize import Browser

br = Browser()
br.set_handle_robots(False)

fernet = Fernet(settings.KEY)
# Create your views here.
def home(request):
    if request.method=="POST":
        if "signup-form" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            #if password doesn't match
            if password != password2:
                msg="Please make sure you're using the same password"
                messages.error(request,msg) 
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(username=username).exists():
                msg="{username} already exists"
                messages.error(request,msg)
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(email=email).exists():
                msg="{email} already exists"
                messages.error(request,msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username,email,password)
                new_user = authenticate(request, username= username,email=email, password= password2)
                if new_user is not None:
                    login(request,new_user)
                    msg = "f{username}.Thanks for subscribing"
                    messages.error(request,msg)
                    return HttpResponseRedirect(request.path)
        elif "logout" in request.POST:
            msg = "{request.user}You logged out"
            logout(request)
            messages.error(request,msg)
            return HttpResponseRedirect(request.path)
        elif "login-form" in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            new_login = authenticate(request, username= username,password=password)
            if new_login is None:
                msg= f"login failed! Make sure you are using the same credentials"
                messages.error(request,msg)
                return HttpResponseRedirect(request.path)
            else:
                code = str(random.randint(100000,999999))
                global global_code
                global_code = code
                send_mail(
                    #subject
                    "Django Password Manager : Confirm Email",
                    f"verifciation code is {code}.",
                    #sender
                    settings.EMAIL_HOST_USER,
                    [new_login.email],
                    fail_silently=False
                )
                return render(request, "home.html",{
                    "code":code,
                    "user":new_login,
                })
        elif "confirm" in request.POST.get("code"):
            input_code = request.POST.get("code")
            user = request.POST.get("user")
            if input_code != global_code:
                msg= f"{input_code} is wrong. Make sure you are using code sent to your gmail account"
                messages.error(request,msg)
                return HttpResponseRedirect(request.path)
            else:
                login(request, user.objects.get(username=user))
                msg= f"Welcome Again"
                messages.success(request,msg)
                return HttpResponseRedirect(request.path)
        elif "add-password" in request.POST:
            url = request.POST.get("url")
            email = request.POST.get("email")
            password = request.POST.get("password")

            #encrypting the email and password
            encrypted_email = fernet.encrypt(email.encode())
            encrypted_password = fernet.encrypt(password.encode())

            #get title of website
            br.open(url)
            title= br.title()

            #get the logo's url
            icon = favicon.get(url)[0].url
            #print data
            print("\n\n\n")
            print(encrypted_email)
            print(encrypted_password)
            print(title)
            print(icon)
    return render(request,"home.html")