"""
A series of tests to establish that the command-line managment tools work as
advertised - especially with regards to the handling of the DJANGO_SETTINGS_MODULE
and default settings.py files.
"""
import os
import unittest
import shutil
import sys
import re

from django import conf, bin, get_version
from django.conf import settings

from regressiontests.utils.app_test import AppTestCase

class AdminScriptTestCase(AppTestCase):
    pass

##########################################################################
# DJANGO ADMIN TESTS
# This first series of test classes checks the environment processing
# of the django-admin.py script
##########################################################################


class DjangoAdminNoSettings(AdminScriptTestCase):
    "A series of tests for django-admin.py when there is no settings.py file."

    def test_builtin_command(self):
        "no settings: django-admin builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'environment variable DJANGO_SETTINGS_MODULE is undefined')

    def test_builtin_with_bad_settings(self):
        "no settings: django-admin builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "no settings: django-admin builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")


class DjangoAdminDefaultSettings(AdminScriptTestCase):
    """A series of tests for django-admin.py when using a settings.py file that
    contains the test application.
    """
    def setUp(self):
        self.write_settings('settings.py')

    def tearDown(self):
        self.remove_settings('settings.py')

    def test_builtin_command(self):
        "default: django-admin builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'environment variable DJANGO_SETTINGS_MODULE is undefined')

    def test_builtin_with_settings(self):
        "default: django-admin builtin commands succeed if settings are provided as argument"
        args = ['sqlall','--settings=settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_environment(self):
        "default: django-admin builtin commands succeed if settings are provided in the environment"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_bad_settings(self):
        "default: django-admin builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "default: django-admin builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_custom_command(self):
        "default: django-admin can't execute user commands if it isn't provided settings"
        args = ['noargs_command']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_settings(self):
        "default: django-admin can execute user commands if settings are provided as argument"
        args = ['noargs_command', '--settings=settings']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_environment(self):
        "default: django-admin can execute user commands if settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_django_admin(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

class DjangoAdminFullPathDefaultSettings(AdminScriptTestCase):
    """A series of tests for django-admin.py when using a settings.py file that
    contains the test application specified using a full path.
    """
    def setUp(self):
        self.write_settings('settings.py', INSTALLED_APPS=['django.contrib.auth', 'django.contrib.contenttypes', 'regressiontests.admin_scripts'])

    def tearDown(self):
        self.remove_settings('settings.py')

    def test_builtin_command(self):
        "fulldefault: django-admin builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'environment variable DJANGO_SETTINGS_MODULE is undefined')

    def test_builtin_with_settings(self):
        "fulldefault: django-admin builtin commands succeed if a settings file is provided"
        args = ['sqlall','--settings=settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_environment(self):
        "fulldefault: django-admin builtin commands succeed if the environment contains settings"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_bad_settings(self):
        "fulldefault: django-admin builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "fulldefault: django-admin builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_custom_command(self):
        "fulldefault: django-admin can't execute user commands unless settings are provided"
        args = ['noargs_command']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_settings(self):
        "fulldefault: django-admin can execute user commands if settings are provided as argument"
        args = ['noargs_command', '--settings=settings']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_environment(self):
        "fulldefault: django-admin can execute user commands if settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_django_admin(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

class DjangoAdminMinimalSettings(AdminScriptTestCase):
    """A series of tests for django-admin.py when using a settings.py file that
    doesn't contain the test application.
    """
    def setUp(self):
        self.write_settings('settings.py', INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes'])

    def tearDown(self):
        self.remove_settings('settings.py')

    def test_builtin_command(self):
        "minimal: django-admin builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'environment variable DJANGO_SETTINGS_MODULE is undefined')

    def test_builtin_with_settings(self):
        "minimal: django-admin builtin commands fail if settings are provided as argument"
        args = ['sqlall','--settings=settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'App with label admin_scripts could not be found')

    def test_builtin_with_environment(self):
        "minimal: django-admin builtin commands fail if settings are provided in the environment"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'settings')
        self.assertNoOutput(out)
        self.assertOutput(err, 'App with label admin_scripts could not be found')

    def test_builtin_with_bad_settings(self):
        "minimal: django-admin builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "minimal: django-admin builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_custom_command(self):
        "minimal: django-admin can't execute user commands unless settings are provided"
        args = ['noargs_command']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_settings(self):
        "minimal: django-admin can't execute user commands, even if settings are provided as argument"
        args = ['noargs_command', '--settings=settings']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_environment(self):
        "minimal: django-admin can't execute user commands, even if settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_django_admin(args,'settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

class DjangoAdminAlternateSettings(AdminScriptTestCase):
    """A series of tests for django-admin.py when using a settings file
    with a name other than 'settings.py'.
    """
    def setUp(self):
        self.write_settings('alternate_settings.py')

    def tearDown(self):
        self.remove_settings('alternate_settings.py')

    def test_builtin_command(self):
        "alternate: django-admin builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'environment variable DJANGO_SETTINGS_MODULE is undefined')

    def test_builtin_with_settings(self):
        "alternate: django-admin builtin commands succeed if settings are provided as argument"
        args = ['sqlall','--settings=alternate_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_environment(self):
        "alternate: django-admin builtin commands succeed if settings are provided in the environment"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'alternate_settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_bad_settings(self):
        "alternate: django-admin builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "alternate: django-admin builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_custom_command(self):
        "alternate: django-admin can't execute user commands unless settings are provided"
        args = ['noargs_command']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_settings(self):
        "alternate: django-admin can execute user commands if settings are provided as argument"
        args = ['noargs_command', '--settings=alternate_settings']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_environment(self):
        "alternate: django-admin can execute user commands if settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_django_admin(args,'alternate_settings')
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")


class DjangoAdminMultipleSettings(AdminScriptTestCase):
    """A series of tests for django-admin.py when multiple settings files
    (including the default 'settings.py') are available. The default settings
    file is insufficient for performing the operations described, so the
    alternate settings must be used by the running script.
    """
    def setUp(self):
        self.write_settings('settings.py', INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes'])
        self.write_settings('alternate_settings.py')

    def tearDown(self):
        self.remove_settings('settings.py')
        self.remove_settings('alternate_settings.py')

    def test_builtin_command(self):
        "alternate: django-admin builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'environment variable DJANGO_SETTINGS_MODULE is undefined')

    def test_builtin_with_settings(self):
        "alternate: django-admin builtin commands succeed if settings are provided as argument"
        args = ['sqlall','--settings=alternate_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_environment(self):
        "alternate: django-admin builtin commands succeed if settings are provided in the environment"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'alternate_settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_bad_settings(self):
        "alternate: django-admin builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "alternate: django-admin builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_custom_command(self):
        "alternate: django-admin can't execute user commands unless settings are provided"
        args = ['noargs_command']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_settings(self):
        "alternate: django-admin can't execute user commands, even if settings are provided as argument"
        args = ['noargs_command', '--settings=alternate_settings']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_environment(self):
        "alternate: django-admin can't execute user commands, even if settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_django_admin(args,'alternate_settings')
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")


class DjangoAdminSettingsDirectory(AdminScriptTestCase):
    """
    A series of tests for django-admin.py when the settings file is in a
    directory. (see #9751).
    """

    def setUp(self):
        self.write_settings('settings', is_dir=True)

    def tearDown(self):
        self.remove_settings('settings', is_dir=True)

    def test_setup_environ(self):
        "directory: startapp creates the correct directory"
        test_dir = os.path.dirname(os.path.dirname(__file__))
        args = ['startapp','settings_test']
        out, err = self.run_django_admin(args,'settings')
        self.assertNoOutput(err)
        self.assert_(os.path.exists(os.path.join(test_dir, 'settings_test')))
        shutil.rmtree(os.path.join(test_dir, 'settings_test'))

    def test_builtin_command(self):
        "directory: django-admin builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'environment variable DJANGO_SETTINGS_MODULE is undefined')

    def test_builtin_with_bad_settings(self):
        "directory: django-admin builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "directory: django-admin builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_custom_command(self):
        "directory: django-admin can't execute user commands unless settings are provided"
        args = ['noargs_command']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_builtin_with_settings(self):
        "directory: django-admin builtin commands succeed if settings are provided as argument"
        args = ['sqlall','--settings=settings', 'admin_scripts']
        out, err = self.run_django_admin(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_environment(self):
        "directory: django-admin builtin commands succeed if settings are provided in the environment"
        args = ['sqlall','admin_scripts']
        out, err = self.run_django_admin(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')


##########################################################################
# MANAGE.PY TESTS
# This next series of test classes checks the environment processing
# of the generated manage.py script
##########################################################################

class ManageNoSettings(AdminScriptTestCase):
    "A series of tests for manage.py when there is no settings.py file."

    def test_builtin_command(self):
        "no settings: manage.py builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_builtin_with_bad_settings(self):
        "no settings: manage.py builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_builtin_with_bad_environment(self):
        "no settings: manage.py builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")


class ManageDefaultSettings(AdminScriptTestCase):
    """A series of tests for manage.py when using a settings.py file that
    contains the test application.
    """
    def setUp(self):
        self.write_settings('settings.py')

    def tearDown(self):
        self.remove_settings('settings.py')

    def test_builtin_command(self):
        "default: manage.py builtin commands succeed when default settings are appropriate"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_settings(self):
        "default: manage.py builtin commands succeed if settings are provided as argument"
        args = ['sqlall','--settings=settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_environment(self):
        "default: manage.py builtin commands succeed if settings are provided in the environment"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_bad_settings(self):
        "default: manage.py builtin commands succeed if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "default: manage.py builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'bad_settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_custom_command(self):
        "default: manage.py can execute user commands when default settings are appropriate"
        args = ['noargs_command']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_settings(self):
        "default: manage.py can execute user commands when settings are provided as argument"
        args = ['noargs_command', '--settings=settings']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_environment(self):
        "default: manage.py can execute user commands when settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_manage(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")


class ManageFullPathDefaultSettings(AdminScriptTestCase):
    """A series of tests for manage.py when using a settings.py file that
    contains the test application specified using a full path.
    """
    def setUp(self):
        self.write_settings('settings.py', INSTALLED_APPS=['django.contrib.auth', 'django.contrib.contenttypes', 'regressiontests.admin_scripts'])

    def tearDown(self):
        self.remove_settings('settings.py')

    def test_builtin_command(self):
        "fulldefault: manage.py builtin commands succeed when default settings are appropriate"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_settings(self):
        "fulldefault: manage.py builtin commands succeed if settings are provided as argument"
        args = ['sqlall','--settings=settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_environment(self):
        "fulldefault: manage.py builtin commands succeed if settings are provided in the environment"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_bad_settings(self):
        "fulldefault: manage.py builtin commands succeed if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "fulldefault: manage.py builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'bad_settings')
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_custom_command(self):
        "fulldefault: manage.py can execute user commands when default settings are appropriate"
        args = ['noargs_command']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_settings(self):
        "fulldefault: manage.py can execute user commands when settings are provided as argument"
        args = ['noargs_command', '--settings=settings']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_environment(self):
        "fulldefault: manage.py can execute user commands when settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_manage(args,'settings')
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

class ManageMinimalSettings(AdminScriptTestCase):
    """A series of tests for manage.py when using a settings.py file that
    doesn't contain the test application.
    """
    def setUp(self):
        self.write_settings('settings.py', INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes'])

    def tearDown(self):
        self.remove_settings('settings.py')

    def test_builtin_command(self):
        "minimal: manage.py builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'App with label admin_scripts could not be found')

    def test_builtin_with_settings(self):
        "minimal: manage.py builtin commands fail if settings are provided as argument"
        args = ['sqlall','--settings=settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'App with label admin_scripts could not be found')

    def test_builtin_with_environment(self):
        "minimal: manage.py builtin commands fail if settings are provided in the environment"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'settings')
        self.assertNoOutput(out)
        self.assertOutput(err, 'App with label admin_scripts could not be found')

    def test_builtin_with_bad_settings(self):
        "minimal: manage.py builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "minimal: manage.py builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, 'App with label admin_scripts could not be found')

    def test_custom_command(self):
        "minimal: manage.py can't execute user commands without appropriate settings"
        args = ['noargs_command']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_settings(self):
        "minimal: manage.py can't execute user commands, even if settings are provided as argument"
        args = ['noargs_command', '--settings=settings']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_environment(self):
        "minimal: manage.py can't execute user commands, even if settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_manage(args,'settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

class ManageAlternateSettings(AdminScriptTestCase):
    """A series of tests for manage.py when using a settings file
    with a name other than 'settings.py'.
    """
    def setUp(self):
        self.write_settings('alternate_settings.py')

    def tearDown(self):
        self.remove_settings('alternate_settings.py')

    def test_builtin_command(self):
        "alternate: manage.py builtin commands fail with an import error when no default settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_builtin_with_settings(self):
        "alternate: manage.py builtin commands fail if settings are provided as argument but no defaults"
        args = ['sqlall','--settings=alternate_settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_builtin_with_environment(self):
        "alternate: manage.py builtin commands fail if settings are provided in the environment but no defaults"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'alternate_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_builtin_with_bad_settings(self):
        "alternate: manage.py builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_builtin_with_bad_environment(self):
        "alternate: manage.py builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_custom_command(self):
        "alternate: manage.py can't execute user commands"
        args = ['noargs_command']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_custom_command_with_settings(self):
        "alternate: manage.py can't execute user commands, even if settings are provided as argument"
        args = ['noargs_command', '--settings=alternate_settings']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")

    def test_custom_command_with_environment(self):
        "alternate: manage.py can't execute user commands, even if settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_manage(args,'alternate_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Can't find the file 'settings.py' in the directory containing './manage.py'")


class ManageMultipleSettings(AdminScriptTestCase):
    """A series of tests for manage.py when multiple settings files
    (including the default 'settings.py') are available. The default settings
    file is insufficient for performing the operations described, so the
    alternate settings must be used by the running script.
    """
    def setUp(self):
        self.write_settings('settings.py', INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes'])
        self.write_settings('alternate_settings.py')

    def tearDown(self):
        self.remove_settings('settings.py')
        self.remove_settings('alternate_settings.py')

    def test_builtin_command(self):
        "multiple: manage.py builtin commands fail with an import error when no settings provided"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'App with label admin_scripts could not be found.')

    def test_builtin_with_settings(self):
        "multiple: manage.py builtin commands succeed if settings are provided as argument"
        args = ['sqlall','--settings=alternate_settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, 'CREATE TABLE')

    def test_builtin_with_environment(self):
        "multiple: manage.py builtin commands fail if settings are provided in the environment"
        # FIXME: This doesn't seem to be the correct output.
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'alternate_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, 'App with label admin_scripts could not be found.')

    def test_builtin_with_bad_settings(self):
        "multiple: manage.py builtin commands fail if settings file (from argument) doesn't exist"
        args = ['sqlall','--settings=bad_settings', 'admin_scripts']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Could not import settings 'bad_settings'")

    def test_builtin_with_bad_environment(self):
        "multiple: manage.py builtin commands fail if settings file (from environment) doesn't exist"
        args = ['sqlall','admin_scripts']
        out, err = self.run_manage(args,'bad_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "App with label admin_scripts could not be found")

    def test_custom_command(self):
        "multiple: manage.py can't execute user commands using default settings"
        args = ['noargs_command']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")

    def test_custom_command_with_settings(self):
        "multiple: manage.py can execute user commands if settings are provided as argument"
        args = ['noargs_command', '--settings=alternate_settings']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand")

    def test_custom_command_with_environment(self):
        "multiple: manage.py can execute user commands if settings are provided in environment"
        args = ['noargs_command']
        out, err = self.run_manage(args,'alternate_settings')
        self.assertNoOutput(out)
        self.assertOutput(err, "Unknown command: 'noargs_command'")


class ManageValidate(AdminScriptTestCase):
    def tearDown(self):
        self.remove_settings('settings.py')

    def test_nonexistent_app(self):
        "manage.py validate reports an error on a non-existent app in INSTALLED_APPS"
        self.write_settings('settings.py', INSTALLED_APPS=['admin_scriptz.broken_app'], USE_I18N=False)
        args = ['validate']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'No module named admin_scriptz')

    def test_broken_app(self):
        "manage.py validate reports an ImportError if an app's models.py raises one on import"
        self.write_settings('settings.py', INSTALLED_APPS=['admin_scripts.broken_app'])
        args = ['validate']
        out, err = self.run_manage(args)
        self.assertNoOutput(out)
        self.assertOutput(err, 'ImportError')

    def test_complex_app(self):
        "manage.py validate does not raise an ImportError validating a complex app with nested calls to load_app"
        self.write_settings('settings.py',
            INSTALLED_APPS=['admin_scripts.complex_app', 'admin_scripts.simple_app'],
            DEBUG=True)
        args = ['validate']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, '0 errors found')

    def test_app_with_import(self):
        "manage.py validate does not raise errors when an app imports a base class that itself has an abstract base"
        self.write_settings('settings.py',
            INSTALLED_APPS=['admin_scripts.app_with_import', 'django.contrib.comments'],
            DEBUG=True)
        args = ['validate']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, '0 errors found')

##########################################################################
# COMMAND PROCESSING TESTS
# Check that user-space commands are correctly handled - in particular,
# that arguments to the commands are correctly parsed and processed.
##########################################################################

class CommandTypes(AdminScriptTestCase):
    "Tests for the various types of base command types that can be defined."
    def setUp(self):
        self.write_settings('settings.py')

    def tearDown(self):
        self.remove_settings('settings.py')

    def test_version(self):
        "--version is handled as a special case"
        args = ['--version']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        # Only check the first part of the version number
        self.assertOutput(out, get_version().split('-')[0])

    def test_help(self):
        "--help is handled as a special case"
        args = ['--help']
        out, err = self.run_manage(args)
        if sys.version_info < (2, 5):
            self.assertOutput(out, "usage: manage.py subcommand [options] [args]")
        else:
            self.assertOutput(out, "Usage: manage.py subcommand [options] [args]")
        self.assertOutput(err, "Type 'manage.py help <subcommand>' for help on a specific subcommand.")

    def test_specific_help(self):
        "--help can be used on a specific command"
        args = ['sqlall','--help']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "Prints the CREATE TABLE, custom SQL and CREATE INDEX SQL statements for the given model module name(s).")

    def test_base_command(self):
        "User BaseCommands can execute when a label is provided"
        args = ['base_command','testlabel']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel',), options=[('option_a', '1'), ('option_b', '2'), ('option_c', '3'), ('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_base_command_no_label(self):
        "User BaseCommands can execute when no labels are provided"
        args = ['base_command']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=(), options=[('option_a', '1'), ('option_b', '2'), ('option_c', '3'), ('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_base_command_multiple_label(self):
        "User BaseCommands can execute when no labels are provided"
        args = ['base_command','testlabel','anotherlabel']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel', 'anotherlabel'), options=[('option_a', '1'), ('option_b', '2'), ('option_c', '3'), ('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_base_command_with_option(self):
        "User BaseCommands can execute with options when a label is provided"
        args = ['base_command','testlabel','--option_a=x']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel',), options=[('option_a', 'x'), ('option_b', '2'), ('option_c', '3'), ('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_base_command_with_options(self):
        "User BaseCommands can execute with multiple options when a label is provided"
        args = ['base_command','testlabel','-a','x','--option_b=y']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel',), options=[('option_a', 'x'), ('option_b', 'y'), ('option_c', '3'), ('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_noargs(self):
        "NoArg Commands can be executed"
        args = ['noargs_command']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:NoArgsCommand options=[('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_noargs_with_args(self):
        "NoArg Commands raise an error if an argument is provided"
        args = ['noargs_command','argument']
        out, err = self.run_manage(args)
        self.assertOutput(err, "Error: Command doesn't accept any arguments")

    def test_app_command(self):
        "User AppCommands can execute when a single app name is provided"
        args = ['app_command', 'auth']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:AppCommand app=<module 'django.contrib.auth.models'")
        self.assertOutput(out, os.sep.join(['django','contrib','auth','models.py']))
        self.assertOutput(out, "'>, options=[('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_app_command_no_apps(self):
        "User AppCommands raise an error when no app name is provided"
        args = ['app_command']
        out, err = self.run_manage(args)
        self.assertOutput(err, 'Error: Enter at least one appname.')

    def test_app_command_multiple_apps(self):
        "User AppCommands raise an error when multiple app names are provided"
        args = ['app_command','auth','contenttypes']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:AppCommand app=<module 'django.contrib.auth.models'")
        self.assertOutput(out, os.sep.join(['django','contrib','auth','models.py']))
        self.assertOutput(out, "'>, options=[('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")
        self.assertOutput(out, "EXECUTE:AppCommand app=<module 'django.contrib.contenttypes.models'")
        self.assertOutput(out, os.sep.join(['django','contrib','contenttypes','models.py']))
        self.assertOutput(out, "'>, options=[('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_app_command_invalid_appname(self):
        "User AppCommands can execute when a single app name is provided"
        args = ['app_command', 'NOT_AN_APP']
        out, err = self.run_manage(args)
        self.assertOutput(err, "App with label NOT_AN_APP could not be found")

    def test_app_command_some_invalid_appnames(self):
        "User AppCommands can execute when some of the provided app names are invalid"
        args = ['app_command', 'auth', 'NOT_AN_APP']
        out, err = self.run_manage(args)
        self.assertOutput(err, "App with label NOT_AN_APP could not be found")

    def test_label_command(self):
        "User LabelCommands can execute when a label is provided"
        args = ['label_command','testlabel']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:LabelCommand label=testlabel, options=[('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

    def test_label_command_no_label(self):
        "User LabelCommands raise an error if no label is provided"
        args = ['label_command']
        out, err = self.run_manage(args)
        self.assertOutput(err, 'Enter at least one label')

    def test_label_command_multiple_label(self):
        "User LabelCommands are executed multiple times if multiple labels are provided"
        args = ['label_command','testlabel','anotherlabel']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:LabelCommand label=testlabel, options=[('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")
        self.assertOutput(out, "EXECUTE:LabelCommand label=anotherlabel, options=[('pythonpath', None), ('settings', None), ('traceback', None), ('verbosity', '1')]")

class ArgumentOrder(AdminScriptTestCase):
    """Tests for 2-stage argument parsing scheme.

    django-admin command arguments are parsed in 2 parts; the core arguments
    (--settings, --traceback and --pythonpath) are parsed using a Lax parser.
    This Lax parser ignores any unknown options. Then the full settings are
    passed to the command parser, which extracts commands of interest to the
    individual command.
    """
    def setUp(self):
        self.write_settings('settings.py', INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes'])
        self.write_settings('alternate_settings.py')

    def tearDown(self):
        self.remove_settings('settings.py')
        self.remove_settings('alternate_settings.py')

    def test_setting_then_option(self):
        "Options passed after settings are correctly handled"
        args = ['base_command','testlabel','--settings=alternate_settings','--option_a=x']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel',), options=[('option_a', 'x'), ('option_b', '2'), ('option_c', '3'), ('pythonpath', None), ('settings', 'alternate_settings'), ('traceback', None), ('verbosity', '1')]")

    def test_setting_then_short_option(self):
        "Short options passed after settings are correctly handled"
        args = ['base_command','testlabel','--settings=alternate_settings','--option_a=x']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel',), options=[('option_a', 'x'), ('option_b', '2'), ('option_c', '3'), ('pythonpath', None), ('settings', 'alternate_settings'), ('traceback', None), ('verbosity', '1')]")

    def test_option_then_setting(self):
        "Options passed before settings are correctly handled"
        args = ['base_command','testlabel','--option_a=x','--settings=alternate_settings']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel',), options=[('option_a', 'x'), ('option_b', '2'), ('option_c', '3'), ('pythonpath', None), ('settings', 'alternate_settings'), ('traceback', None), ('verbosity', '1')]")

    def test_short_option_then_setting(self):
        "Short options passed before settings are correctly handled"
        args = ['base_command','testlabel','-a','x','--settings=alternate_settings']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel',), options=[('option_a', 'x'), ('option_b', '2'), ('option_c', '3'), ('pythonpath', None), ('settings', 'alternate_settings'), ('traceback', None), ('verbosity', '1')]")

    def test_option_then_setting_then_option(self):
        "Options are correctly handled when they are passed before and after a setting"
        args = ['base_command','testlabel','--option_a=x','--settings=alternate_settings','--option_b=y']
        out, err = self.run_manage(args)
        self.assertNoOutput(err)
        self.assertOutput(out, "EXECUTE:BaseCommand labels=('testlabel',), options=[('option_a', 'x'), ('option_b', 'y'), ('option_c', '3'), ('pythonpath', None), ('settings', 'alternate_settings'), ('traceback', None), ('verbosity', '1')]")
