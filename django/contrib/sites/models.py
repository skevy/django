from django.db import models
from django.utils.translation import ugettext_lazy as _

SITE_CACHE = {}
CURRENT_SITE = {}

class SiteManager(models.Manager):
    def get_current(self):
        """
        Returns the current ``Site`` based on the SITE_ID in the
        project's settings. The ``Site`` object is cached the first
        time it's retrieved from the database.
        """
        global CURRENT_SITE
        
        if CURRENT_SITE:
            return CURRENT_SITE
            
        from django.conf import settings
        try:
            sid = settings.SITE_ID
        except AttributeError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("You're using the Django \"sites framework\" without having set the SITE_ID setting. Create a site in your database and set the SITE_ID setting to fix this error.")
        try:
            site = SITE_CACHE[sid]
            CURRENT_SITE = site
        except KeyError:
            site = self.get(pk=sid)
            SITE_CACHE[sid] = site
            CURRENT_SITE = site
        return site

    def clear_cache(self):
        """Clears the ``Site`` object cache."""
        global SITE_CACHE
        SITE_CACHE = {}
        
    def get_from_host(self, request, check_subdomain=True):
        """
        Returns the ``Site`` which matches the host name retreived from
        ``request``.

        If no match is found and ``check_subdomain`` is ``True``, the sites are
        searched again for sub-domain matches.

        If still no match, or if more than one ``Site`` matched the host name, a
        ``RequestSite`` object is returned.

        The returned ``Site`` or ``RequestSite`` object is cached for the host
        name retrieved from ``request``.
        """ 
        global CURRENT_SITE
        host = request.get_host().lower()
        #print host
        if host in SITE_CACHE:
            # The host name was found in cache, return it. A cache value
            # of None means that a RequestSite should just be used.
            CURRENT_SITE = SITE_CACHE[host] or RequestSite(request)
            return CURRENT_SITE
        matches = Site.objects.filter(domain__iexact=host)
        # We use len rather than count to save a second query if there was only
        # one matching Site
        count = len(matches)
        if not count and check_subdomain:
            matches = []
            for site in Site.objects.all():
                if host.endswith(site.domain.lower()):
                    matches.append(site)
            count = len(matches)
        if count == 1:
            # Return the single matching Site
            site = matches[0]
        else:
            site = None
        # Cache the site (caching None means we should use RequestSite).
        CURRENT_SITE = SITE_CACHE[host] = site
        # Return site, falling back to just using a RequestSite.
        return CURRENT_SITE or RequestSite(request)

class Site(models.Model):
    domain = models.CharField(_('domain name'), max_length=100)
    name = models.CharField(_('display name'), max_length=50)
    objects = SiteManager()

    class Meta:
        db_table = 'django_site'
        verbose_name = _('site')
        verbose_name_plural = _('sites')
        ordering = ('domain',)

    def __unicode__(self):
        return self.domain

    def save(self, *args, **kwargs):
        super(Site, self).save(*args, **kwargs)
        # Cached information will likely be incorrect now.
        if self.id in SITE_CACHE:
            del SITE_CACHE[self.id]

    def delete(self):
        pk = self.pk
        super(Site, self).delete()
        try:
            del SITE_CACHE[pk]
        except KeyError:
            pass

class RequestSite(object):
    """
    A class that shares the primary interface of Site (i.e., it has
    ``domain`` and ``name`` attributes) but gets its data from a Django
    HttpRequest object rather than from a database.

    The save() and delete() methods raise NotImplementedError.
    """
    def __init__(self, request):
        self.domain = self.name = request.get_host()

    def __unicode__(self):
        return self.domain

    def save(self, force_insert=False, force_update=False):
        raise NotImplementedError('RequestSite cannot be saved.')

    def delete(self):
        raise NotImplementedError('RequestSite cannot be deleted.')
