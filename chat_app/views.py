from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout

# def room_name(request):
#     return render(request, 'chat/enter_room_name.html')
# def room(request, room_name):
#     return render(request, 'chat/chat.html', {'room_name': room_name})



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage

@login_required
def home(request):
    user_1 = request.user
    
    # Unread message count
    unread_msg = ChatMessage.count_overall_unread_msg(user_1.id)

    # Exclude logged-in user for available users list
    all_users = User.objects.exclude(id=user_1.id)

    # Get the user's chat sessions
    user_all_friends = ChatSession.objects.filter(Q(user1=user_1) | Q(user2=user_1)).select_related('user1', 'user2').order_by('-updated_on')

    all_friends = []
    for ch_session in user_all_friends:
        user, user_1= [ch_session.user2, ch_session.user1] if user_1.username == ch_session.user1.username else [ch_session.user1, ch_session.user2]
        un_read_msg_count = ChatMessage.objects.filter(chat_session=ch_session.id, message_detail__read=False).exclude(user=user_1).count()

        all_friends.append({
            "user_name": user.username,
            "room_name": ch_session.room_group_name,
            "un_read_msg_count": un_read_msg_count,
            "status": user.profile_detail.is_online,
            "user_id": user.id
        })

    # Handle adding a new friend
    if request.GET.get('add_friend'):
        user2_id = request.GET.get('add_friend')
        user_2 = get_object_or_404(User, id=user2_id)
        created = ChatSession.create_if_not_exists(user_1, user_2)

        msg = f'{user_2.username} successfully added to your chat list!!' if created else f'{user_2.username} is already in your chat list!!'
        messages.add_message(request, messages.SUCCESS, msg)

        return HttpResponseRedirect('/home')

    # Handle opening a chat
    if request.GET.get('chat'):
        room_name = request.GET.get('chat')
        session_id = room_name[5:]  # Extract session ID

        chat_session = ChatSession.objects.filter(Q(id=session_id) & (Q(user1=user_1) | Q(user2=user_1))).first()
        if not chat_session:
            return HttpResponse("You don't have permission to chat with this user!!!")

        opposite_user = chat_session.user2 if chat_session.user1 == user_1 else chat_session.user1
        fetch_all_messages = ChatMessage.objects.filter(chat_session=chat_session).order_by('message_detail__timestamp')

        return render(request, 'chat/start_chat.html', {
            'room_name': room_name,
            'opposite_user': opposite_user,
            'fetch_all_message': fetch_all_messages
        })

    # Handle fetching the last message
    if request.GET.get('last_msg'):
        session_id = request.GET.get('last_msg')
        last_message = ChatMessage.objects.filter(chat_session__id=session_id).last()
        return HttpResponse(last_message.message_detail if last_message else "No messages found", status=200 if last_message else 404)

    return render(request, 'chat/home.html', {
        "unread_msg": unread_msg,
        "all_users": all_users,
        "user_list": all_friends
    })

# @login_required
# def friend_list(request):
#     user_inst = request.user
#     user_all_friends = ChatSession.objects.filter(Q(user1 = user_inst) | Q(user2 = user_inst)).select_related('user1','user2').order_by('-updated_on')
#     all_friends = []
#     for ch_session in user_all_friends:
#         user,user_inst = [ch_session.user2,ch_session.user1] if request.user.username == ch_session.user1.username else [ch_session.user1,ch_session.user2]
#         un_read_msg_count = ChatMessage.objects.filter(chat_session = ch_session.id,message_detail__read = False).exclude(user = user_inst).count()        
#         data = {
#             "user_name" : user.username,
#             "room_name" : ch_session.room_group_name,
#             "un_read_msg_count" : un_read_msg_count,
#             "status" : user.profile_detail.is_online,
#             "user_id" : user.id
#         }
#         all_friends.append(data)

#     return render(request, 'chat/friend_list.html', {'user_list': all_friends})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home page after signup
    else:
        form = UserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the