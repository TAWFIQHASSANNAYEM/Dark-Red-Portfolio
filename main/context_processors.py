from .models import Profile, SiteSettings


def site_settings(request):
    """
    Context processor to make site settings and profile available globally.
    """
    return {
        'site_settings': SiteSettings.objects.first(),
        'profile': Profile.objects.first(),
    }
