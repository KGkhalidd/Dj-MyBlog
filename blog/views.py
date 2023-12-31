from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage , PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm , SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery , SearchRank, TrigramSimilarity
# from django.http import Http404
# Create your views here.

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET :
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity= TrigramSimilarity('title', query),
            ).filter(similarity__gt= 0.1).order_by('-similarity')

    context= {
        'form':form,
        'query':query,
        'results': results
    }
    return render(request, 'blog/post/search.html', context)


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

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 2
#     template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None ):
    post_list= Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 3) #make the page have 3 from post list
    page_number = request.GET.get('page', 1) # brings page num from request 'the page that displays the posts'
    try:
        posts = paginator.page(page_number) # depends on the page num it will brings the posts in this page
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts':posts , 'tag': tag,})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
                            Post,
                            status= Post.Status.PUBLISHED,
                            slug=post, #slug of the post = post that in the request url in urls.py
                            publish__year= year,
                            publish__month= month,
                            publish__day= day
                            )
    
    comments = post.comments.filter(active=True)
    form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in = post_tags_ids).exclude(id=post.id)
    similar_posts= similar_posts.annotate(same_tags = Count('tags')).order_by('-same_tags','-publish')[:4]
    context = {
        'post':post,
        'comments':comments,
        'form':form ,
        'similar_posts':similar_posts ,
        }
    return render(request, 'blog/post/detail.html', context)

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
    # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()

    context = {
        'post': post,
        'form': form,
        'comment': comment
        }
    return render(request, 'blog/post/comment.html', context)

