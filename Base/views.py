from django.shortcuts import render,redirect
from .models import Room,Topic,Message,User
from django.contrib import messages
from .forms import RoomForm,MyUserCreationForm,MyUserUpdationForm
from django.contrib.auth.decorators import login_required
from  django.db.models import Q
from django.contrib.auth import authenticate,login,logout

def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('Home')
    
    context={'page':page}
    if request.method=='POST':
        username=request.POST.get('email').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(email=username)
        except:
            messages.error(request,"User does not exist")
        else:
            user=authenticate(request,username=username,password=password)

            if user is not None:
                login(request,user)
                return redirect('Home')
            else:
                messages.error(request,"Username or password does not exist")

    return render(request,'login_register.html',context)

def logoutPage(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('Home')

    messages.error(request,"Please login first")
    return render(request,"ErrorPage.html")

def signupPage(request):

    if request.user.is_authenticated:
        return redirect('Home')
    
    if request.method=='POST':
        form=MyUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.name=user.name.lower()
            user.save()
            login(request,user)
            return redirect('Home')
        else:
            messages.error(request,"Registration failed!")
            messages.error(request,"1.try using a unique username")
            messages.error(request,"2.Ensure passwords match!")
            print(form.errors)
    
    form=MyUserCreationForm()
    page='signup'
    context={'page':page,'form':form}
    
    return render(request,'login_register.html',context)

def home(request):
    topics=Topic.objects.all()[:5]
    topic_name=request.GET.get('q') if request.GET.get('q') else ''
    if topic_name!='':
        rooms=Room.objects.filter(Q(topic__name__icontains=topic_name) |
                              Q(name__icontains=topic_name) |
                              Q(description__icontains=topic_name))
    else:
        rooms=Room.objects.all()    
        
    room_count=rooms.count()    
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=topic_name))[:5] 
    for room_msg in room_messages:
        if len(room_msg.body)>30:
            room_msg.body=room_msg.body[:30]+"..."                  
    context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,"home.html",context)

def topics(request):
    topic_search=request.GET.get('q') if request.GET.get('q') else ''
    topics=Topic.objects.filter(name__icontains=topic_search)
    
    context={
        'topics':topics
    } 
    return render(request,"topics.html",context)

def activity(request):
    activities=Message.objects.all()
    context={
        'room_messages':activities
    }
    return render(request,"activity.html",context)

def room(request,room_id):
    room=Room.objects.get(id=room_id)
    
    if  request.method=='POST':
        if not request.user.is_authenticated:
            return redirect('login')
        if len(request.POST.get('body'))!=0:
            obj=Message(user=request.user,room=room,body=request.POST.get('body'))
            obj.save()
            room.participants.add(request.user)
        else:
            messages.error(request,"Post can't be empty")    
    
    participants=set() 
    room_messages=Message.objects.filter(room_id=room_id).order_by('-updated')
    for user_msg in room_messages:
        participants.add(user_msg.user)
    participants=list(participants) 
    participants_count=len(participants)   
    context={'room':room,'room_messages':room_messages,'participants':participants,'participants_count':participants_count}    
    return render(request,"room.html",context)

@login_required(login_url='login')
def create_room(request):
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        room=Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        room.save()
        return redirect('Home')
    form=RoomForm()
    topics=Topic.objects.all()
    context={'form':form,'topics':topics }
    return render(request,"new_room.html",context)

@login_required(login_url='login')
def update_room(request,room_id):
    room=Room.objects.get(id=room_id)
    
    if request.user != room.host:
        messages.error(request,"You don't have the privledge to update")
        return render(request,"ErrorPage.html")
    
    if request.method=='POST':
        room=Room.objects.get(id=room_id)
        room.description=request.POST.get('description')
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        room.topic=topic
        room.name=request.POST.get('name')
        room.save()
        return redirect('Home')
        
    topics=Topic.objects.all()
    room=Room.objects.get(id=room_id)
    form=RoomForm(instance=room)
    context={'form':form,'topics':topics,'room':room}
    return render(request,'new_room.html',context)    

@login_required(login_url='login')
def delete_room(request,room_id):
    room=Room.objects.get(id=room_id)
    
    if request.user!=room.host:
        messages.error(request,"You don't have the privledge to delete")
        return render(request,"ErrorPage.html")
    
    if request.method=="POST":
        room.delete()
        return redirect('Home')
    
    context={'obj':room}
    return render(request,"delete.html",context)    

@login_required(login_url='login')
def delete_comment(request,msg_id,room_id):
    msg=Message.objects.get(id=msg_id)
    context={
        'obj':msg,
    }
    
    if request.user!=msg.user:
        messages.error(request,"You don't have the privledge to delete")
        return render(request,"ErrorPage.html")

    if request.method=="POST":
        msg.delete()
        return redirect('Room',room_id)
    
    return render(request,"delete.html",context)

@login_required(login_url='login') #not implemented but has urls and template ready: edit_comment.html
def edit_comment(request,msg_id,room_id):
    msg=Message.objects.get(id=msg_id)
    context={
        'message':msg,
    }
    
    if request.user!=msg.user:
        messages.error(request,"You don't have the privledge to edit")
        return render(request,"ErrorPage.html")
    
    if request.method=="POST" and len(request.POST.get('comment'))!=0:
        msg.body=request.POST.get('comment') 
        msg.save()
        return redirect('Room',room_id)
    
    return render(request,"edit_comment.html",context)

@login_required(login_url='login')
def delete_activity(request,msg_id):
    msg=Message.objects.get(id=msg_id)
    context={
        'obj':msg.body,
    }
    
    if request.user!=msg.user:
        messages.error(request,"You don't have the privledge to delete")
        return render(request,"ErrorPage.html")
        
    if request.method=="POST":
        msg.delete()
        return redirect('Home')
    
    return render(request,"delete.html",context)

@login_required(login_url='login')
def userProfile(request,id):
    user=User.objects.get(id=id)
    topics=Topic.objects.all()
    user_activity=Message.objects.filter(user__id=id)
    user_rooms=Room.objects.filter(host__id=id)
    context={'user':user,'topics':topics,'room_messages':user_activity,'rooms':user_rooms}
    return render(request,'profile.html',context)

@login_required(login_url='login')
def updateUser(request):
    if not request.user.is_authenticated:
        messages.error(request,"You don't have the privledge to update")
        return render(request,"ErrorPage.html")
    
    user=request.user
    form=MyUserUpdationForm(instance=user)
    
    if request.method=='POST':
        form=MyUserUpdationForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',user.id)
        else:
            messages.error(request,"Could not update info!")
            #print(form.errors)     debud info
    
    context={'form':form}
    return render(request,"update-user.html",context)

def page_not_found(request,exception):
    return render(request,"404.html")