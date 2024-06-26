from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User, auth 
from django.contrib import messages 
from .models import Profile,Post,LikePost,FollowersCount
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from itertools import chain
import random

# Create your views here.
User = get_user_model()

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))


    return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def settings(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_profile.bio = request.POST.get('bio', user_profile.bio)
        user_profile.location = request.POST.get('location', user_profile.location)
        if 'image' in request.FILES:
            user_profile.profileimg = request.FILES['image']
        user_profile.save()
        return redirect('settings')

    return render(request, 'settings.html', {'user_profile': user_profile})


@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST.get('caption')

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST.get('username')
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user = ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))

    return render(request,'search.html',{'user_profile':user_profile,'username_profile_list':username_profile_list})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username 
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id,username=username).first()
    
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id,username=username)
        new_like.save()
        post.no_of_likes += 1 
        post.save()
        return redirect('/')
    
    else:
        like_filter.delete()
        post.no_of_likes -= 1 
        post.save()
        return redirect('/')
    
    
@login_required(login_url='signin')
def profile(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile = get_object_or_404(Profile, user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    # Initialize these variables outside the if-else block
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST.get('follower')
        user = request.POST.get('user')

        if FollowersCount.objects.filter(follower=follower,user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            return redirect('/profile/' + user) 
        else:
            new_follower = FollowersCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.info(request, "Passwords are not matching")
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email Taken')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.info(request, "Username Taken")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        #log in user and redirect to the settings page 
        user_login = auth.authenticate(username=username,password=password)
        auth.login(request,user_login)

        #Create a profile for the user 
        user_model = User.objects.get(username=username)
        new_profile = Profile.objects.create(user=user_model,id_user=user_model.id)
        new_profile.save()
        # You might want to redirect to a login page or to the homepage with a success message
        messages.success(request, "User created successfully")
        return redirect('settings')  # Assuming you have a 'login' route defined

    else:
        return render(request, 'signup.html')

def signin(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            # If authentication fails, inform the user and render the same signin page
            messages.info(request, "Invalid Credentials")
            return redirect(signin)  # Ensure this return here to handle failed authentication

    else:
        # This handles GET requests and any other methods that might be used to access the page
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

