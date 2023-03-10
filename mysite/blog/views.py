from django.shortcuts import render, get_object_or_404
from .models import Post,PublishedManager, Comment
from django.core.paginator import Paginator, EmptyPage, \
PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


 
# Create your views here.
def post_list(request,  tag_slug=None):
    object_list = Post.published.all()
    tag = None
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    Post.objects.annotate(search=SearchVector('title', 'body'),).filter(search='django')

    if tag_slug:
         tag = get_object_or_404(Tag, slug=tag_slug)
         object_list = object_list.filter(tags__in=[tag])

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
        
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
   
    comments = post.comments.filter(active=True)

    new_comment = None
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts  = Post.published.filter(tags__in=post_tags_ids).exclude(id =post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    Post.objects.annotate(search=SearchVector('title', 'body'),).filter(search='django')


    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
        # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
        # Assign the current post to the comment
            new_comment.Post = post
        # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form, 'similar_posts': similar_posts})
    
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    Post.objects.annotate(search=SearchVector('title', 'body'),).filter(search='django')


def Post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            
        # form fields passed validation
             cd = form.cleaned_data
             post_url = request.build_absolute_uri(post.get_absolute_url())  
             subject = f"{cd['name']} recommends you read " \
                       f"{post.title}"
             message = f"read {post.title} at {post_url}\n\n " \
                      f"{cd ['name']}\'s commends :  {cd['comments']}" 
             send_mail(subject, message, 'omarfathy@myblog.com', [cd['to']])      
             sent = True     
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent })    


def post_search(request):
    form  = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            results = Post.published.annotate(search = search_vector, rank = SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')

    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results':results})

         