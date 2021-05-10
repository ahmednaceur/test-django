from django.http import JsonResponse
from django.shortcuts import render,redirect
from rest_framework import generics, status, views, permissions
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.utils import json

from .serializers import RegisterSerializer, EmailVerificationSerializer, LoginSerializer, LogoutSerializer, \
      LinkSerializer
from rest_framework.generics import ListAPIView, CreateAPIView, get_object_or_404

from django.views import View


from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User  ,Link
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util


# Register API

@authentication_classes(())
@permission_classes((AllowAny,))
class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()

            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])
            token = RefreshToken.for_user(user).access_token

            current_site = get_current_site(request).domain
            relativeLink = reverse('email-verify')
            absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
            email_body = 'Hi '+user.username + \
                ' Use the link below to verify your email \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Verify your email'}

            Util.send_email(data)
            return Response(user_data, status=status.HTTP_201_CREATED)
        except:
            return Response({'error': 'User already exsit '}, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes(())
@permission_classes((AllowAny,))
class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes(())
@permission_classes((AllowAny,))
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

#ici liste des lien created selon chaque user
class ShortenerListAPIView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        email_user = request.data.get("email_user")
        if email_user is None  :
            return Response({'error': 'Please provide email_user'},
                            status.HTTP_400_BAD_REQUEST)
        queryset=Link.Objects.filter(email_user=email_user).values()
        serializer_class=LinkSerializer
        return Response(queryset,status=status.HTTP_204_NO_CONTENT)

#ici cette view c'est pour create le link modifier
class ShortenerCreateApiView(CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class=LinkSerializer


#cette view et pour tt persone qui click va le redericte vers sont lien cree et on meme temp il va calcule les click
class Redirector(View):

    def get(self, request, shortener_link, *args, **kwargs):

            shortener_link = settings.HOST_URL + '/' + self.kwargs['shortener_link']
            redirect_link=shortener_link
            try:
                redirect_link = Link.Objects.filter(shortened_link=shortener_link).first().original_link
                id = Link.Objects.filter(shortened_link=shortener_link).first().id
                count =Link.Objects.filter(shortened_link=shortener_link).first().clicks
                link   = get_object_or_404(Link, id=id)
                link.clicks=count+1
                link.save()
                return redirect(redirect_link)
            except:
                return redirect(redirect_link)

