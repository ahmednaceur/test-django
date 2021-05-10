
from django.urls import path

from .views import RegisterView, LogoutAPIView, VerifyEmail, LoginAPIView,  ShortenerCreateApiView, ShortenerListAPIView, Redirector


urlpatterns = [

    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('AllLink',ShortenerListAPIView.as_view(),name='all_links'),
    path('createLink/',ShortenerCreateApiView.as_view(),name='create_api'),
    path('<str:shortener_link>/', Redirector.as_view(), name='redirector')

]
