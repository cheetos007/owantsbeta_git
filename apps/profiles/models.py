from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from sorl.thumbnail import ImageField
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.core.cache import cache

from emailconfirmation.models import EmailAddress
from idios.models import ProfileBase
from social_auth.signals import pre_update
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends import USERNAME

from urlparse import urlparse
import urllib2

from profiles import PROFILE_CACHE_TIMEOUT, PROFILE_CACHE_KEY

DEFAULT_PROFILE_IMAGE = "default_avatar.png"
class Profile(ProfileBase):
    about = models.TextField(_("about"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=40, null=True, blank=True)
    website = models.URLField(_("website"), null=True, blank=True, verify_exists=False)
    image = models.ImageField(_("image"), null=True, blank=True, upload_to="user_profiles/%y/%m/%d", default=DEFAULT_PROFILE_IMAGE)
    last_ip = models.CharField(_("last IP address"), blank=True, max_length=16)
    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         if self.user.email:
    #             EmailAddress.objects.add_email(self.user, self.user.email)
    #         if self.user.first_name or self.user.last_name:
    #             self.name = '%s %s' % (self.user.first_name, self.user_last_name)

    #     return super(Profile, self).save(*args, **kwargs)

@receiver(models.signals.post_save, sender=Profile)
def update_cache(sender, instance, **kwargs):
    cache.set('%s_%d' % (PROFILE_CACHE_KEY, instance.user_id), instance, PROFILE_CACHE_TIMEOUT)

@receiver(models.signals.post_delete, sender=Profile)
def delete_cache(sender, instance, **kwargs):
    cache.delete('%s_%d' % (PROFILE_CACHE_KEY, instance.user_id))

original_get_profile = User.get_profile

def get_profile(self):
    if not hasattr(self,'_profile_cache'):
        profile = cache.get('%s_%s' % (PROFILE_CACHE_KEY, self.pk))
        if not profile:
            profile = original_get_profile(self)
            if profile:
                cache.set('%s_%s' % (PROFILE_CACHE_KEY, self.pk), profile, PROFILE_CACHE_TIMEOUT)
        self._profile_cache = profile
        self._profile_cache.user = self
    return self._profile_cache

User.get_profile = get_profile

def get_full_name(self):
    """
    Monkeypatching User.get_full_name to return username if neither first nor last name are specified
    """
    if self.first_name or self.last_name:
        full_name = u'%s %s' % (self.first_name, self.last_name)
    else:
        full_name = self.username
    return full_name.strip()

User.get_full_name = get_full_name

def update_user_base_data(user, details):
    for name, value in details.iteritems():
        # do not update username, it was already generated
        if name in (USERNAME, 'id', 'pk'):
            continue
        if value and (getattr(user, name, None) in (None, '')):
            setattr(user, name, value)

def twitter_extra_values(sender, user, response, details, **kwargs):
    update_user_base_data(user, details)
    user.save()
    profile = user.get_profile()
    profile.name = user.get_full_name()

    try:
        img_url = response['profile_image_url']
        image_name = urlparse(img_url).path.split('/')[-1]
        profile.image.save(image_name, ContentFile(urllib2.urlopen(img_url).read()))
    except (urllib.HTTPError, KeyError):
        pass
    profile.save()
    return True

pre_update.connect(twitter_extra_values, sender=TwitterBackend)

def facebook_extra_values(sender, user, response, details, **kwargs):

    #avoid circular imports
    from invite_friends.facebook import facebook_factory, FacebookAPIError

    update_user_base_data(user, details)
    user.save()
    profile = user.get_profile()
    profile.name = user.get_full_name()

    if profile.image=='' or profile.image==DEFAULT_PROFILE_IMAGE:
        try:
            fb = facebook_factory()
            img = fb.get_profile_picture(response['access_token'], response['id'])
            if img:
                profile.image.save(*img)
        except FacebookAPIError:
            pass

    profile.save()
    if user.emailaddress_set.count()==0:
        EmailAddress.objects.get_or_create(user=user, email=user.email, primary=True)
    return True

pre_update.connect(facebook_extra_values, sender=FacebookBackend)

@receiver(user_logged_in)
def update_ip(sender, request, user, **kwargs):
    if not 'REMOTE_ADDR' in request.META:
        return
    profile = user.get_profile()
    profile.last_ip = request.META['REMOTE_ADDR']
    profile.save()

