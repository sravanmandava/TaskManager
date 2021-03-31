from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    return render(request,'tasks/home.html')


def signupuser(request):
    if request.method == "GET":
        return render(request,'tasks/signupuser.html',{'form':UserCreationForm()})
    else:
        #creating a user
        if request.POST['username'] == "":
            return render(request,'tasks/signupuser.html',{'form':UserCreationForm(),'error':"Please enter a valid username"})


        if request.POST['password1'] == request.POST['password2']:
            try:
                user=User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('currenttasks')
            except IntegrityError:
                return render(request,'tasks/signupuser.html',{'form':UserCreationForm(),'error':"Username already exists.Choose a new username"})
        else:
            #tell user that passwords didn't match
            return render(request,'tasks/signupuser.html',{'form':UserCreationForm(),'error':"Passwords did not match"})

def loginuser(request):
    if request.method == "GET":
        return render(request,'tasks/loginuser.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request,'tasks/loginuser.html',{'form':AuthenticationForm(),'error':"Usename and password didn't match. Try Again"})
        else:
            login(request,user)
            return redirect('currenttasks')

@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')

@login_required
def createtask(request):
    if request.method == "GET":
        return render(request,'tasks/createtask.html',{'form':TaskForm()})
    else:
        try:
            form =TaskForm(request.POST)
            newtask=form.save(commit=False)
            newtask.user=request.user
            newtask.save()
            return redirect('currenttasks')
        except ValueError:
            return render(request,'tasks/createtask.html',{'form':TaskForm(),'error':"Bad data Passed in.Try Again"})

@login_required
def currenttasks(request):
    tasks=Task.objects.filter(user=request.user,datecompleted__isnull=True)
    return render(request,'tasks/currenttasks.html',{'tasks':tasks})

@login_required
def completedtasks(request):
    tasks=Task.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'tasks/completedtasks.html',{'tasks':tasks})


@login_required
def viewtask(request,task_pk):
    task=get_object_or_404(Task,pk=task_pk,user=request.user)
    if request.method == "GET":
        form=TaskForm(instance=task)
        return render(request,'tasks/viewtask.html',{'task':task,'form':form})
    else:
        try:
            form =TaskForm(request.POST,instance=task)
            form.save()
            return redirect('currenttasks')
        except ValueError:
            return render(request,'tasks/viewtask.html',{'task':task,'form':form,'error':"Bad Info"})

@login_required
def completetask(request,task_pk):
    task=get_object_or_404(Task,pk=task_pk,user=request.user)
    if request.method == "POST":
        task.datecompleted = timezone.now()
        task.save()
        return redirect('currenttasks')

@login_required
def deletetask(request,task_pk):
    task=get_object_or_404(Task,pk=task_pk,user=request.user)
    if request.method == "POST":
        task.delete()
        return redirect('currenttasks')
