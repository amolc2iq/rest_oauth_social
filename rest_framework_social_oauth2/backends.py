# -*- coding: utf-8 -*-

try:
    from django.urls import reverse
except ImportError:  # Will be removed in Django 2.0
    from django.core.urlresolvers import reverse

from social_core.backends.oauth import BaseOAuth2
from .settings import DRFSO2_PROPRIETARY_BACKEND_NAME, DRFSO2_URL_NAMESPACE

from oauth2_provider.models import AccessToken
from social_django.models import UserSocialAuth
from django.contrib.auth.models import User

class DjangoOAuth2(BaseOAuth2):
    """Default OAuth2 authentication backend used by this package"""
    name = DRFSO2_PROPRIETARY_BACKEND_NAME
    AUTHORIZATION_URL = reverse(DRFSO2_URL_NAMESPACE + ':authorize'
                                if DRFSO2_URL_NAMESPACE else 'authorize')
    ACCESS_TOKEN_URL = reverse(DRFSO2_URL_NAMESPACE + ':token'
                               if DRFSO2_URL_NAMESPACE else 'authorize')

    def get_user_details(self, response):
        print(response)
        if response.get(self.ID_KEY, None):
            user = User.objects.get(pk=response[self.ID_KEY])
            return {
                     'username': user.username,
                     'email': user.email,
                     'fullname': user.get_full_name(),
                     'first_name': user.first_name,
                     'last_name': user.last_name
                    }
        return {}

    def user_data(self, access_token, *args, **kwargs):
        try:
            user_id = UserSocialAuth.objects.filter(extra_data__contains=access_token).first()# AccessToken.objects.get(token=access_token).user.pk
            return {self.ID_KEY: user_id.user.id}
        except AccessToken.DoesNotExist:
            return None

    def do_auth(self, access_token, *args, **kwargs):
        """Finish the auth process once the access_token was retrieved"""
        data = self.user_data(access_token, *args, **kwargs)
        
        response = kwargs.get('response') or {}
        response.update(data or {})
        kwargs.update({'response': response, 'backend': self})
        if response.get(self.ID_KEY, None):
            user = User.objects.get(pk=response[self.ID_KEY])
            return user
        else:
            return None

    