from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
# Create your views here.

def post_list(request):
    posts= Post.published.all()
    return render(request, 'blog/post/list.html', {'posts':posts})

def post_detail(request, year, month, day, post):
    # try:
    #     #the first id is from database
    #     post= Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404('No Post found.')
    
    post = get_object_or_404(Post,
                            status= Post.Status.PUBLISHED,
                            slug=post, #slug of the post = post that in the request url in urls.py
                            publish__year= year,
                            publish__month= month,
                            publish__day= day)
    
    return render(request, 'blog/post/detail.html', {'post':post})
