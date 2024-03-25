from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, Document
from .forms import RoomForm, UserForm, MyUserCreationForm, CodeSnippetForm, DocumentForm
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import traceback
import os

# Create your views here.

# rooms = [
#     {'id':1, 'name':'lets learn python'},
#     {'id':2, 'name':'Backend developers'},
#     {'id':3, 'name':'Frontend developers'},
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except: 
            messages.error(request, 'user does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None: 
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password does not exist')

    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
        )

    topics = Topic.objects.all()[0:5]

    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        'rooms': rooms, 
        'topics': topics, 
        'room_count': room_count,
        'room_messages': room_messages
          }
    return render(request, 'base/home.html', context)

def room(request, id):

    room = Room.objects.get(id=id) 
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', id=room.id)

    context = {
        'room' : room , 
        'room_messages' : room_messages, 
        'participants' : participants
        }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def code_editor(request):
    form = CodeSnippetForm(request.POST or None)
    output = None
    if request.method == 'POST':
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                # Redirect stdout to capture output
                import sys
                from io import StringIO
                original_stdout = sys.stdout
                sys.stdout = StringIO()
                exec(code)
                output = sys.stdout.getvalue()
                # Restore stdout
                sys.stdout = original_stdout
            except Exception as e:
                output = f"Error: {e}<br>{traceback.format_exc()}"
            return JsonResponse({'output': output})
    return render(request, 'base/code-editor.html', {'form': form})


@login_required(login_url='login')
def save_code(request):
    if request.method == 'POST':
        form = CodeSnippetForm(request.POST)
        if form.is_valid():
            code_snippet = form.save()  # Save the code snippet to the database
            return JsonResponse({'success': True, 'id': code_snippet.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'errors': 'Invalid request method'})

def google_meet_auth(request):
    # Generate authorization URL
    auth_url = "https://accounts.google.com/o/oauth2/auth?"
    auth_url += "response_type=code"
    auth_url += "&client_id=484745872524-0bspvhjro0fon5o907qpoeirhuuusccb.apps.googleusercontent.com"
    auth_url += "&redirect_uri=https://www.joint-dev.com"
    auth_url += "&scope=https://www.googleapis.com/auth/meet.readonly"

    return redirect(auth_url)

@login_required(login_url='login')
def google_meet_callback(request):
    # Get authorization code from request
    code = request.GET.get('code')

    # Exchange authorization code for access token
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "code": code,
        "client_id": "484745872524-0bspvhjro0fon5o907qpoeirhuuusccb.apps.googleusercontent.com",
        "client_secret": "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",
        "redirect_uri": "https://www.joint-dev.com",
        "grant_type": "authorization_code"
    }
    response = google_requests.post(token_url, data=token_payload)
    token_data = response.json()
    access_token = token_data.get("access_token")

    # Now you can use this access_token to make requests to Google Meet API
    # e.g., list upcoming meetings
    # ...

    return HttpResponse("Successfully authenticated with Google Meet.")


def list_upcoming_meetings(access_token):
    url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()
    

def google_meet_view(request):
    # Pass the URL to the template
    # meeting_id = str(uuid.uuid4())
    # meet_url = "https://meet.google.com/{meeting_id}"
    meet_url = "https://meet.google.com/?authuser=0"
    return render(request, 'base/meet.html', {'meet_url':meet_url})


def joinMeeting(request):
    return render(request, 'base/video_conference.html')

def userProfile(request, id):
    user = User.objects.get(id=id)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user,
               'rooms': rooms,
               'room_messages': room_messages,
               'topics': topics
               }
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user, 
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse(' Forbidden!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, id):
    room = Room.objects.get(id=id)

    if request.user != room.host:
        return HttpResponse(' Forbidden!!')


    if request.method == 'POST':
        room.delete()
        return redirect ('home')
    return render (request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def deleteMessage(request, id):
    message = Message.objects.get(id=id)

    if request.user != message.user:
        return HttpResponse(' Forbidden!!')


    if request.method == 'POST':
        message.delete()
        return redirect ('home')
    return render (request, 'base/delete.html', {'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form. is_valid():
            form.save()
            return redirect('user-profile', id=user.id)

    return render(request, 'base/update-user.html', {'form':form})



def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})
    

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages}) 



# def repo(request):
#     documents = Document.objects.all()
#     # notes = Note.objects.all()
#     file_extensions = [document.file.name.split('.')[-1].lower() for document in documents]
#     return render(request, 'base/repo.html', {'documents': documents, 'file_extensions': file_extensions})

# def add_document(request):
#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('repo')
#     else:
#         form = DocumentForm()
#     return render(request, 'base/add_document.html', {'form': form})

# def delete_document(request, document_id):
#     document = Document.objects.get(id=document_id)
#     document.delete()
#     return redirect('repo')
@login_required(login_url='login')
def repo(request):
    documents = Document.objects.all()
    return render(request, 'base/repo.html', {'documents': documents})

@login_required(login_url='login')
def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('repo')
    else:
        form = DocumentForm()
    return render(request, 'base/add_document.html', {'form': form})

@login_required(login_url='login')
def delete_document(request, document_id):
    document = Document.objects.get(id=document_id)
    document.delete()
    return redirect('repo')