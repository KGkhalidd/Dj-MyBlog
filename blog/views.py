from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage , PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail
# from django.http import Http404
# Create your views here.


def post_share(request, post_id):

    post = get_object_or_404(Post, id= post_id, status=Post.Status.PUBLISHED)
    sent = False #will be used to track if the email has been successfully sent.

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # If the submitted form data passes validation
            # Extract the cleaned data from the form
            cd = form.cleaned_data # this holds form inputs
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'khaledgamal1345@gmail.com',[cd['to']])
            sent= True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent,
                                                    })

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'

# def post_list(request):
#     post_list= Post.published.all()
#     paginator = Paginator(post_list, 2) #make the page have 3 from post list
#     page_number = request.GET.get('page', 1) # brings page num from request 'the page that displays the posts'
#     try:
#         posts = paginator.page(page_number) # depends on the page num it will brings the posts in this page
#     except PageNotAnInteger:
#         # If page_number is not an integer deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page_number is out of range deliver last page of results
#         posts = paginator.page(paginator.num_pages)
#     return render(request, 'blog/post/list.html', {'posts':posts})

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



