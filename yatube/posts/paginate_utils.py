from django.conf import settings
from django.core.paginator import Paginator


def paginate_posts(post_list, request):
    paginator = Paginator(post_list, settings.PAGINATION_ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
