from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Count
from django.forms import formset_factory
from django.shortcuts import render, get_object_or_404, redirect

from .forms import *

reportsMaxNo = 3
commentMaxNo = 5


def index(request):
    return render(request, 'home.html')


# ---------------------------------------------------------------------------------------------
@login_required
def category_projects(request, id):
    category_pro = []
    projects = Projects.objects.filter(category_id=id)
    for i in projects:
        images = Images.objects.filter(project_id=i.id)
        category_pro.append({'project': i, 'images': images})
    return render(request, 'category.html', {'category_projects': category_pro})


# ---------------------------------------------------------------------------------------------
# search bar
@login_required
def search(request):
    found_projects = []
    word = request.POST['search']
    if word[0] == '#':
        word = word[1:]
        projects = Projects.objects.filter(tags__tags=word)
    else:
        projects = Projects.objects.filter(title__icontains=word)
    for i in projects:
        images = Images.objects.filter(project_id=i.id)
        found_projects.append({'project': i, 'images': images})
    return render(request, 'Search.html', {'found_projects': found_projects})


# ---------------------------------------------------------------------------------------------

# delete Project
@login_required
def delete(request, id):
    Projects.objects.get(pk=id).delete()
    return redirect(index)


# ---------------------------------------------------------------------------------------------
# report Project
@login_required
def report(request, id):
    session_user = request.user.id
    Projectdata = Projects.objects.get(pk=id)
    user = User.objects.get(pk=session_user)
    report = ProjectReport(user_id=user, project_id=Projectdata)
    report.save()
    if ProjectReport.objects.filter(project_id=id).count() > reportsMaxNo:
        return redirect(delete, id=id)
    else:
        return redirect(viewdataofproject, id=id)


# ---------------------------------------------------------------------------------------------
# delete Comment
@login_required
def deleteComment(request, id, project_id):
    Comment.objects.get(pk=id).delete()
    return redirect(viewdataofproject, id=project_id)


# ---------------------------------------------------------------------------------------------
# reportComment
@login_required
def reportComment(request, id, project_id):
    session_user = request.user.id
    comment = Comment.objects.get(pk=id)
    user = User.objects.get(pk=session_user)
    report = Reportno(user_id=user, comment_id=comment)
    report.save()
    if Reportno.objects.filter(comment_id=id).count() > commentMaxNo:
        return redirect(deleteComment, id=id)
    else:
        return redirect(viewdataofproject, id=project_id)


# ---------------------------------------------------------------------------------------------
@login_required
def rate(request, id):
    if request.method == 'POST':
        form = addRating(request.POST)
        if form.is_valid():
            try:
                rate = Rating.objects.get(project_id=get_object_or_404(Projects, pk=id),
                                          user_id=get_object_or_404(User, pk=request.user.id))
                value =form.save(commit=False)
                rate.rating = value.rating
                rate.save()
            except:
                rate = form.save(commit=False)
                rate.project_id = get_object_or_404(Projects, pk=id)
                rate.user_id = get_object_or_404(User, pk=request.user.id)
                rate.save()
    return redirect(viewdataofproject, id=id)


# ---------------------------------------------------------------------------------------------
@login_required
def donate(request, id):
    session_user = request.user.id
    if request.method == 'POST':
        form = addDonation(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.user_id = get_object_or_404(User, id=session_user)
            donation.project_id = get_object_or_404(Projects, pk=id)
            donation.save()
    return redirect(viewdataofproject, id=id)


# ---------------------------------------------------------------------------------------------
@login_required
def comment(request, id):
    session_user = request.user.id
    if request.method == 'POST':
        form = Addcommentinproject(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user_id = get_object_or_404(User, id=session_user)
            comment.project_id = get_object_or_404(Projects, pk=id)
            comment.save()
    return redirect(viewdataofproject, id=id)


# ---------------------------------------------------------------------------------------------
# Similar Projects => ordinary function
def recommend(id):
    project = Projects.objects.get(pk=id)
    tags = project.tags.all()
    similar = Projects.objects.exclude(pk=id).filter(tags__in=tags).annotate(counts=Count('title')).order_by('-counts')[
              :5]
    return similar


# ---------------------------------------------------------------------------------------------
@login_required
def viewdataofproject(request, id):
    session_user = request.user.id
    Projectdata = Projects.objects.get(pk=id)
    user = User.objects.get(id=session_user)
    categories = Categories.objects.all()
    user_id = Projectdata.user_id.id

    dict = Donation.objects.filter(project_id=id).aggregate(sum=Sum('amount_of_money'))
    authority = ''

    if user_id == session_user:  # session id here
        if dict['sum'] is None or dict['sum'] <= .25 * Projects.objects.get(id=id).total_target:
            authority = "cancel"
    else:
        if not ProjectReport.objects.filter(user_id=session_user).exists():
            authority = "report"

    form = Addcommentinproject()
    rate = addRating()
    donate = addDonation()
    tags = Projectdata.tags.all()
    image = Images.objects.filter(project_id=id)
    rating = Rating.objects.all().filter(project_id=id).aggregate(Avg('rating'))
    comments = Comment.objects.filter(project_id=id)
    context = {
        "authority": authority,
        "Projectdata": Projectdata,
        "total_donation": dict['sum'],
        "tags": tags,
        "image": image,
        "rate": rating['rating__avg'],
        'form': form,
        'comments': comments,
        'rate_form': rate,
        'donate_form': donate,
        'currentUser': session_user,
        'similar_projects': recommend(id),
        'categories': categories
    }
    return render(request, 'dataofProject.html', context)


# ordinary function
def addtag(i):
    if Tags.objects.filter(tags=i).exists():
        return Tags.objects.get(tags=i)
    else:
        tag = Tags(tags=i)
        tag.save()
        return tag


@login_required
def addproject(request):
    session_user = request.user.id
    ImageFormSet = formset_factory(Addimage, extra=3)
    categories = Categories.objects.all()

    if request.method == 'POST':
        form = Addproject(request.POST)
        form2 = ImageFormSet(request.POST, request.FILES)
        if form.is_valid() and form2.is_valid():
            project = form.save(commit=False)
            project.user_id = get_object_or_404(User, id=session_user)
            project.save()

            data = request.POST['tags']
            data = data.split(',')
            for i in data:
                project.tags.add(addtag(i))

            for form in form2.cleaned_data:
                if form:
                    image = form['image']
                    photo = Images(project_id=project, image=image)
                    photo.save()
            return redirect(viewdataofproject, id=project.id)
        else:
            print(form.errors, form2.errors)

    form = Addproject()
    form2 = ImageFormSet()
    context = {"form": form, "form2": form2, 'categories': categories}
    return render(request, 'addproject.html', context)
