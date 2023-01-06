from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


def signup(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('home')
        else:
            messages.error(
                request, 'Ann error occured during signup! Try again')

    context = {'form': form}
    return render(request, 'base/signup.html', context)


def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password').lower()
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Account Doesn't exist")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('home')
        else:
            messages.error(request, 'Password went wrong')
    context = {}
    return render(request, 'base/signin.html', context)


def signout(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(
        name__icontains=q) | Q(description__icontains=q))
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'room_messages': room_messages,
               'room_count': str(len(rooms)), 'text': q}
    return render(request, 'base/home.html', context)


def profile(request, username):
    try:
        profile = User.objects.get(username=username)
    except:
        profile = None

    if profile != None:
        rooms = profile.room_set.all()
        room_messages = profile.message_set.all()
        topics = Topic.objects.all()
        context = {'user': profile, 'rooms': rooms,
                   'room_messages': room_messages, 'topics': topics}
        return render(request, 'base/profile.html', context)
    else:
        return HttpResponse('404')


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == "POST" and request.user.is_authenticated:
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='signin')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        room.participants.set([request.user])
        #     room.participants.add(request.user)
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='signin')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    topic = Topic.objects.all()
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('404')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')
    context = {'form': form, 'room': room, 'topic': topic}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='signin')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('404')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/delete.html', context)


@login_required(login_url='signin')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('404')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'obj': message}
    return render(request, 'base/delete.html', context)


@login_required(login_url='signin')
def editProfile(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=user.username )
    context = {'user': user, 'form': form}
    return render(request, 'base/edituser.html', context)

def topics(request):
    topics = Topic.objects.all()
    return render(request, 'base/topics.html', {'topics':topics})
