from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import User, Post, Comments
from .forms import PostForm
from datetime import date


def studentYear(email):
    admission_year = 2000 + int(email[:2])
    cur_yr, cur_month = date.today().year, date.today().month
    year = cur_yr - admission_year
    if cur_month > 6: year += 1
    return str(year)


def studentBranch(email):
    branch = email[3:5]
    return branch


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exists!')
            return redirect('home')
        

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
            

    return render(request, 'login.html')

def logoutUser(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    posts = Post.objects.filter(Q(title__icontains=q) | Q(description__icontains=q))
    context = {'posts' : posts}
    if (request.user.is_staff == False):
        context['year'] = studentYear(request.user.email)
        context['branch'] = studentBranch(request.user.email)
    return render(request, 'home/home.html', context)


@login_required(login_url='login')
def announcement(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    posts = Post.objects.filter((Q(title__icontains=q) | Q(description__icontains=q)), Q(author__email__exact='anuj.deshmukh17@gmail.com'))
    context = {'posts' : posts}
    if (request.user.is_staff == False):
        context['year'] = studentYear(request.user.email)
        context['branch'] = studentBranch(request.user.email)
    return render(request, 'home/announcement.html', context)


@login_required(login_url='login')
def academic(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    posts = Post.objects.filter((Q(title__icontains=q) | Q(description__icontains=q)), ~Q(author__email__exact='anuj.deshmukh17@gmail.com'))
    context = {'posts' : posts}
    if (request.user.is_staff == False):
        context['year'] = studentYear(request.user.email)
        context['branch'] = studentBranch(request.user.email)
    return render(request, 'home/academic.html', context)


@login_required(login_url='login')
def post(request, pid):
    post = Post.objects.get(id=pid)
    comments = post.comments_set.all()
    context = {'post' : post, 'comments' : comments} 

    if request.method == "POST":
        comment = Comments.objects.create(
            author=request.user,
            post=post,
            body=request.POST.get('body')
        )
        return redirect('post', pid=post.id)

    return render(request, 'home/post.html', context)


@login_required(login_url='login')
def newPost(request):
    if request.user.is_staff == False:
        return HttpResponse('You cannot Post')

    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    return render(request, 'home/post_form.html', {'form' : form})


@login_required(login_url='login')
def updatePost(request, pid):
    if request.user.is_staff == False:
        return HttpResponse('You are not authorized to edit this post')

    post = Post.objects.get(id=pid)
    form = PostForm(instance=post)

    if request.user != post.author:
        return HttpResponse('You are not authorized to edit this post')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'home/post_form.html', {'form' : form})


@login_required(login_url='login')
def deletePost(request, pid):
    if request.user.is_staff == False:
        return HttpResponse('You cannot Delete')

    post = Post.objects.get(id=pid)
    
    if request.user != post.author:
        return HttpResponse('You are not authorized to delete this post')

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'delete.html', {'obj' : post})


@login_required(login_url='login')
def deleteComment(request, cid):
    comment = Comments.objects.get(id=cid)
    
    if request.user != comment.author:
        return HttpResponse('You are not authorized to delete this comment')

    if request.method == 'POST':
        comment.delete()
        return redirect('home')

    return render(request, 'delete.html', {'obj' : comment})


# Create your views here.

