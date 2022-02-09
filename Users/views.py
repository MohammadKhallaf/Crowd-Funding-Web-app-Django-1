import secrets

from django.contrib.auth import (
    login,
    logout
)
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string

from projects.models import *
from .forms import *


# from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def index(request):
    top_5projects = []
    admin_choice = []
    latest_projects = []

    # Categories
    categories = Categories.objects.all()

    # Top rated binding with their images
    top_rated = Rating.objects.values('project_id').annotate(rates=Avg('rating')).order_by('-rates')[:5]
    for i in top_rated:
        project = Projects.objects.get(pk=i['project_id'])
        images = Images.objects.filter(project_id=i['project_id'])
        top_5projects.append({'project': project, 'images': images})

    # Admin choosen projects binding with their images
    admin_choice_query = Choosen_by_Admin.objects.all()[:5]
    for i in admin_choice_query:
        images = Images.objects.filter(project_id=i.id)
        admin_choice.append({'project': i, 'images': images})

    # Latest Added projects
    latest_projects_query = Projects.objects.order_by('-id')[:5]
    for i in latest_projects_query:
        images = Images.objects.filter(project_id=i.id)
        latest_projects.append({'project': i, 'images': images})

    context = {'top5': top_5projects,
               'admin_choice': admin_choice,
               'latest_projects': latest_projects,
               'categories': categories,
               }
    return render(request, 'home.html', context)


@login_required
def profile(request, username):
    user = User.objects.get(username=username)

    id = user.id
    addtionalinfo = Profile.objects.get(user_id=id)
    user_project = Projects.objects.filter(user_id=id)
    categories = Categories.objects.all()

    if user:
        context = {
            'userinfo': user,
            'addtionalinfo': addtionalinfo,
            'userproject': user_project,
            'categories': categories
        }
        return render(request, 'profile.html', context)
    else:
        return render(request, '404.html')


@login_required
def editprofile(request, id):
    user = User.objects.filter(pk=id).update(username=request.POST['username'], email=request.POST['email'])
    addtionalinfo = Profile.objects.filter(user_id=id).update(country=request.POST['country'],
                                                              phone=request.POST['phone'],
                                                              social_media=request.POST['social_media'],
                                                              birth=request.POST['birth'])
    ur = User.objects.get(pk=id)
    return redirect(profile, username=ur.username)


def user_login(request):
    if request.method == 'POST':
        form = userLogin(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            login(request, user)
            # request.session['userobj'] = User.objects.get(username=username)
            # user_info2 = user_info.objects.Profile_set.all()
            return redirect(index)
    else:
        form = userLogin()
    return render(request, "login.html", {"form": form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        form2 = UserProfile(request.POST, request.FILES)
        if form.is_valid() and form2.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            profile = form2.save(commit=False)
            current_user = User.objects.get(username=username)
            profile.user = current_user
            profile.save()
            request.session['username'] = username
            request.session['email'] = form.cleaned_data.get('email')
            # return redirect(user_login)

            return redirect(send_activation)
    else:
        form = UserRegisterForm()
        form2 = UserProfile()
    return render(request, 'register.html', {'form': form, 'form2': form2})


@login_required
def logout_profile(request):
    logout(request)
    return redirect('login')


def send_activation(request):
    user_OTP_key = secrets.token_hex(16)
    print(user_OTP_key)
    domain = request.get_host()
    print("host", domain)
    user_activation_link = f"{domain}/pass/{user_OTP_key}"
    user_mail = request.session['email']
    subject = 'Activation Mail - Funding django2'
    body = f" Hi {request.session['username']} HERE IS YOUR ACTIVATION LINK"
    html_content = render_to_string('mailActive.html', {'mail': user_activation_link})
    msg = EmailMultiAlternatives(subject=subject, body=body, to=[user_mail])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
    request.session['OTP'] = user_OTP_key
    del request.session['username']
    del request.session['email']
    return redirect(user_login)


def check_activation(request, pkey):
    if request.session['OTP'] == pkey:
        return HttpResponse("CHECKED")
    else:
        return ("Soorryyyyyy")
