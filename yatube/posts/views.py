from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


def page_maker(request, object_list):
    return Paginator(
        object_list,
        settings.POST_NUMBER_ON_PAGE).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': page_maker(request, Post.objects.all())
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': page_maker(request, group.posts.all()),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = request.user.is_authenticated and author != request.user and (
        Follow.objects.filter(user=request.user, author=author).exists())
    return render(request, 'posts/profile.html', {
        'following': following,
        'author': author,
        'page_obj': page_maker(request, author.posts.all()),
    })


def post_detail(request, post_id):
    return render(request, 'posts/post_detail.html', {
        'form': CommentForm(request.POST or None),
        'post': get_object_or_404(Post, id=post_id),
    })


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'post': post,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post.id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': page_maker(
            request, Post.objects.filter(author__following__user=request.user))
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username)
