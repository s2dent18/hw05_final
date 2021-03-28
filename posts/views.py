from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page}
    )


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, "new.html", {"form": form})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_post = user.posts.all()
    post_count = user_post.count
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=user).exists()
    )
    paginator = Paginator(user_post, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    follows = user.follower.all().count
    followers = user.following.all().count
    context = {
        "page": page,
        "post_count": post_count,
        "author": user,
        "paginator": paginator,
        "following": following,
        "follows": follows,
        "followers": followers,
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    post_count = post.author.posts.count()
    comments = post.comments.all()
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user,
            author=post.author).exists()
    )
    follows = User.objects.filter(following__user=post.author).count
    followers = User.objects.filter(following__author__username=username).count
    context = {
        "form": CommentForm(),
        "post": post,
        "post_count": post_count,
        "comments": comments,
        "following": following,
        "follows": follows,
        "followers": followers,
        "author": post.author,
    }
    return render(request, "post.html", context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if post.author != request.user:
        return redirect("post", username=username, post_id=post.pk)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username=username, post_id=post.pk)
    return render(
        request,
        "new.html",
        {"is_edit": True, "form": form, "post": post})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username=post.author, post_id=post.id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        return redirect("profile", username=username)
    if author != request.user:
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("profile", username=username)
