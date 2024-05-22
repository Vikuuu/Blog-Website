from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage


def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
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

    context = {"post": post}
    return render(request, "blog/post/detail.html", context)
