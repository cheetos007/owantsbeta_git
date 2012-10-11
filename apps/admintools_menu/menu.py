"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'pinterest.menu.CustomMenu'
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from admin_tools.menu import items, Menu

from admintools_menu import CONFIGURATION_MODELS, USER_CONTENT_MODELS, USER_MODELS

class CustomMenu(Menu):
    """
    Custom Menu for pinterest admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),
            items.ModelList(
                _('Configuration'),**CONFIGURATION_MODELS
            ),
            items.ModelList(
                _('User-generated content'),
                **USER_CONTENT_MODELS
            ),
            items.ModelList(
                _('Users'),
                **USER_MODELS
            ),
            items.AppList(
                _('Advanced')
            ),

        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomMenu, self).init_with_context(context)
