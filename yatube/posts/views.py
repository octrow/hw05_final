from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .paginate_utils import paginate_posts


def index(request):
    post_list = Post.objects.select_related("group", "author")
    page_obj = paginate_posts(post_list, request)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related("author")
    page_obj = paginate_posts(post_list, request)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = (
        request.user.is_authenticated and request.user != author
    ) and author.following.filter(user=request.user).exists()
    posts = author.posts.select_related("group")
    post_count = posts.count()
    page_obj = paginate_posts(posts, request)
    context = {
        "author": author,
        "page_obj": page_obj,
        "post_count": post_count,
        "following": following,
        "followers_count": author.follower.count(),
        "following_count": author.following.count(),
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author").prefetch_related(
            "comments__author"
        ),
        id=post_id,
    )
    context = {
        "post": post,
        "comments": post.comments.select_related("author"),
        "comment_form": CommentForm(),
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        context = {
            "form": form,
        }
        return render(request, "posts/create_post.html", context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", username=request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post.id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if not form.is_valid():
        context = {"form": form}
        return render(request, "posts/create_post.html", context)
    form.save()
    return redirect("posts:post_detail", post_id=post.id)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        post.delete()
        return redirect("posts:profile", username=request.user.username)
    return redirect("posts:post_detail", post_id=post.id)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        context = {
            "form": form,
        }
        return render(request, ("posts:post_detail", post_id), context)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = get_object_or_404(Post, pk=post_id)
    comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related("author").filter(
        author__following__user=request.user
    )
    page_obj = paginate_posts(post_list, request)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user, author__username=username
    ).delete()
    return redirect("posts:profile", username=username)
