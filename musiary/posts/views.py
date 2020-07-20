from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.utils import timezone
from .models import Post
from django.contrib.auth.decorators import login_required

import pafy
import vlc
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def index(request):
    posts = Post.objects.all()
    context = { 'posts': posts }
    return render(request, 'posts/index.html', context)
    
def detail(request, post_id):
    post = Post.objects.get(id=post_id)
    context = { 'post': post }
    return render(request, 'posts/detail.html', context)

@login_required
def new(request):
    return render(request, 'posts/new.html')

@login_required
def create(request):
    user = request.user
    song = request.POST['song']
    tag = request.POST['tag']
    body = request.POST['body']
    post = Post(user=user, song=song, tag=tag, body=body, created_at=timezone.now())
    post.save()
    return redirect('posts:detail', post_id=post.id)

@login_required
def edit(request, post_id):
    try:
        post = Post.objects.get(id=post_id, user=request.user)
    except Post.DoesNotExist:
        return redirect('posts:index')
        
    context = { 'post' : post }
    return render(request, 'posts/edit.html', context)

@login_required   
def update(request, post_id):
    try:
        post = Post.objects.get(id=post_id, user=request.user)
    except Post.DoesNotExist:
        return redirect('posts:index')
        
    post.song = request.POST['song']
    post.tag = request.POST['tag']
    post.body = request.POST['body']
    post.save()
    return redirect('posts:detail', post_id=post.id)

@login_required
def delete(request, post_id):
    try:
        post = Post.objects.get(id=post_id, user=request.user)
    except Post.DoesNotExist:
        return redirect('posts:index')
        
    post.delete()
    return redirect('posts:index')

@login_required
def like(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            
            if request.user in post.liked_users.all():
                post.liked_users.remove(request.user)
            else:
                post.liked_users.add(request.user)
                
            return redirect('posts:detail', post.id)
        
        except Post.DoesNotExist:
            pass
          
    return redirect('posts:index')


#-----------------------------youtube music streaming-----------------------------
DEVELOPER_KEY = 'DEVELOPER KEY'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def pafy_video(video_id):
    url = 'https://www.youtube.com/watch?v={0}'.format(video_id)
    vid = pafy.new(url)

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

  search_response = youtube.search().list(
    q='Hello world',
    part='id,snippet',
    maxResults=options.max_results
  ).execute()

  videos = []
  playlists = []
  channels = []
  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append('%s' % (search_result['id']['videoId']))
    elif search_result['id']['kind'] == 'youtube#channel':
      channels.append('%s' % (search_result['id']['channelId']))

  if videos:
    print('Videos:{0}'.format(videos))
    pafy_video(videos[0])