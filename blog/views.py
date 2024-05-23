from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"


# class PostDetailView(DetailView):
#     model = Post
#     template_name = "blog/post/detail.html"
#     context_object_name = "post"

#     def get_object(self):
#         return get_object_or_404(
#             Post,
#             status=Post.Status.PUBLISHED,
#             slug=self.kwargs.get("post"),
#             publish__year=self.kwargs.get("year"),
#             publish__month=self.kwargs.get("month"),
#             publish__day=self.kwargs.get("day"),
#         )


def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # if out of range, deliver the last page of result.
        posts = paginator.page(paginator.num_pages)
    context = {"posts": posts}
    return render(request, "blog/post/list.html", context)


def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No Post found.")

    # or

    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    comments = post.comments.filter(active=True)
    form = CommentForm()

    context = {"post": post, "comments": comments, "form": form}
    return render(request, "blog/post/detail.html", context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # --- send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(subject, message, "gutswillneverhurtanyone@gmail.com", [cd["to"]])
            sent = True

    else:
        form = EmailPostForm()

    context = {"post": post, "form": form, "sent": sent}
    return render(request, "blog/post/share.html", context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {"post": post, "form": form, "comment": comment}
    return render(request, "blog/post/comment.html", context)
