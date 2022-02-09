from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)
from projects.models import *
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .token import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage  


# from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required 
def index(request):
    top_5projects=[]
    admin_choice=[]  
    latest_projects=[]

    #Categories 
    categories=Categories.objects.all()

    #Top rated binding with their images
    top_rated=Rating.objects.values('project_id').annotate(rates=Avg('rating')).order_by('-rates')[:5]  
    for i in top_rated:
        project=Projects.objects.get(pk=i['project_id'])
        images=Images.objects.filter(project_id=i['project_id'])
        top_5projects.append({'project':project,'images':images})

    #Admin choosen projects binding with their images
    admin_choice_query=Choosen_by_Admin.objects.all()[:5]  
    for i in admin_choice_query:
        images=Images.objects.filter(project_id=i.id)
        admin_choice.append({'project':i,'images':images})

    #Latest Added projects
    latest_projects_query=Projects.objects.order_by('-id')[:5]   
    for i in latest_projects_query:
        images=Images.objects.filter(project_id=i.id)
        latest_projects.append({'project':i,'images':images})
    context={'top5':top_5projects,'admin_choice':admin_choice,
            'latest_projects':latest_projects,'categories':categories}
    return  render(request,'home.html',context)



@login_required
def profile(request, username):
    user = User.objects.get(username = username)
    id = user.id
    addtionalinfo = Profile.objects.get(user_id = id)
    user_project = Projects.objects.filter(user_id = id)
    categories=Categories.objects.all()

    if user:
        context = {
            'userinfo': user,
            'addtionalinfo': addtionalinfo,
            'userproject': user_project,
            'categories':categories
        }
        return render(request, 'profile.html', context)
    else:
        return render(request, '404.html')

@login_required
def editprofile(request, id):
    user = User.objects.filter(pk = id).update(username=request.POST['username'], email=request.POST['email'])
    addtionalinfo = Profile.objects.filter(user_id = id).update(country=request.POST['country'], phone=request.POST['phone'], social_media=request.POST['social_media'],birth=request.POST['birth'])
    ur = User.objects.get(pk = id)
    return redirect(profile, username=ur.username)

def user_login(request):
    if request.method == 'POST':
        form = userLogin(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username,password=password)
            login(request,user)
            user_info = User.objects.get(username=username)
            # user_info2 = user_info.objects.Profile_set.all()
            if user_info.is_active == True:
                
                return redirect(index)
    else:
        form = userLogin()        
    return render(request,"login.html",{"form":form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        form2 = UserProfile(request.POST,request.FILES)
        if form.is_valid() and form2.is_valid():
            pr=form.save(commit=False)
            pr.is_active = False 
            pr.save()
            #pr=form.save(commit=False)
            username = form.cleaned_data.get('username')
            profile = form2.save(commit=False)
            #current_user.is_active = False 
            
            current_user = User.objects.get(username=username)
            
            #pr.save()
            profile.user = current_user
            profile.save()
            current_site = get_current_site(request) 
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('acc_active_email.html', {  
                'user': pr,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(pr.pk)), 
                 'token':account_activation_token.make_token(pr),  
            })   
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                        mail_subject, message, to=[to_email]  
            ) 
            email.send()  
            return HttpResponse('Please confirm your email address to complete the registration')  
              
            # #user = User.objects.get(email=current_user['email'])
            # token= RefreshToken.for_user(current_user)
            # data = {'domain':}
            # Util.send_email(data)

            #return redirect(user_login)
    else:
        form = UserRegisterForm()
        form2 = UserProfile()
    return render(request,'register.html', {'form': form , 'form2':form2})


@login_required
def logout_profile(request):
    logout(request)
    return redirect('login')


def activate(request, uidb64, token):  
    User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        #return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        return redirect(user_login)  
    else:  
        return HttpResponse('Activation link is invalid!') 
         
