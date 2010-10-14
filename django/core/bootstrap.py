from django.core.exceptions import ImproperlyConfigured
from django.utils.exceptions import format_exception
from django.utils.functional import curry
from django.utils.importlib import import_module

__all__ = ['autodiscover', 'bootstrap', 'register', 'REGISTRY']

REGISTRY = []
_BOOTSTRAPPED = False
__BOOTSTRAP_COMPLETE = False

class BootstrapRan(RuntimeError):
    pass

def autodiscover():
    """
    Auto-discover INSTALLED_APPS startup.py modules and fail silently when
    not present. This forces an import on them to evaluate any 
    
    Note: borrowing heavily from django.contrib.admin.autodiscover
    """

    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's startup module.
        try:
            import_module('%s.startup' % app)
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have a startup module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'startup'):
                raise

def register(fn, *args, **kwargs):
    allow_late_registration=kwargs.pop('allow_late_registration', False)

    if args or kwargs:
        reg_fn = curry(fn, *args, **kwargs)
    else:
        reg_fn = fn

    if not __BOOTSTRAP_COMPLETE or allow_late_registration:
        REGISTRY.append(reg_fn)
        if allow_late_registration and __BOOTSTRAP_COMPLETE:
            reg_fn()
    else:
        raise BootstrapRan("Cannot register new bootstrap method; bootstrap has already run.")

def bootstrap():
    global _BOOTSTRAPPED
    global __BOOTSTRAP_COMPLETE

    if not _BOOTSTRAPPED:
        # Before proceeding, mark the bootstrap process as having been run.\n
        # This needs to be done early so we don't spawn infinte loops.
        _BOOTSTRAPPED = True

        from django.conf import settings
        path = settings.BOOTSTRAP_FUNCTION

        if not path:
            return

        i = path.rfind('.')
        module, attr = path[:i], path[i+1:]
        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, format_exception(e)))
        try:
            func = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
        try:
            func()
        except Exception, e:
            import traceback
            raise ImproperlyConfigured("Unable to run bootstrap process. (%s)" % traceback.format_exc())

        for i, fn in enumerate(REGISTRY):
            try:
                fn()
            except Exception, e:
                raise RuntimeError("Bootstrap process failed on registered item %d (%s). Error was %s." % (i, fn, format_exception(e)))

        __BOOTSTRAP_COMPLETE = True
