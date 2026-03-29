from .models import Wishlist

def wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        if not request.session.session_key:
            request.session.create()
        count = Wishlist.objects.filter(
            session_key=request.session.session_key
        ).count()

    return {"wishlist_count": count}