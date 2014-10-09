# -*- coding: utf-8 -*-

from dolmen.forms.base.interfaces import IField
from dolmen.forms.base.markers import ModeMarker
from dolmen.forms.base.widgets import DisplayFieldWidget
from dolmen.forms.ztk.widgets import getTemplate
from dolmen.location import get_absolute_url
from grokcore import component as grok
from zope.interface import Interface


class LinkFieldWidget(DisplayFieldWidget):
    grok.adapts(IField, Interface, Interface)
    grok.name('link')

    template = getTemplate('linkfieldwidget.cpt')
    
    def url(self):
        context = self.form.context
        return get_absolute_url(context, self.request)


LINK = ModeMarker('LINK', extractable=False)
