# URI widget

import re

from dolmen.forms.base.markers import Marker, NO_VALUE
from dolmen.forms.base.widgets import FieldWidget
from dolmen.forms.ztk.fields import BaseField, registerSchemaField
from dolmen.forms.base.widgets import WidgetExtractor
from dolmen.forms.ztk.widgets import getTemplate

from grokcore import component as grok
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces

_ = MessageFactory("dolmen.forms.base")


isURI = re.compile(
    # scheme
    r"[a-zA-z0-9+.-]+:"
    # non space (should be pickier)
    r"\S*$").match


class URIField(BaseField):
    """A text line field.
    """
    target = '_self'

    def __init__(self, title,
                 minLength=0,
                 maxLength=None,
                 **options):
        super(URIField, self).__init__(title, **options)
        self.minLength = minLength
        self.maxLength = maxLength

    def isEmpty(self, value):
        return value is NO_VALUE or not len(value)

    def validate(self, value, form):
        error = super(URIField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker) and len(value):
            assert isinstance(value, basestring)
            if not isURI(value):
                return _(u"The URI is malformed.")
            if self.minLength and len(value) < self.minLength:
                return _(u"The URI is too short.")
            if self.maxLength and len(value) > self.maxLength:
                return _(u"The URI is too long.")
        return None


class DateWidgetExtractor(WidgetExtractor):
    grok.adapts(URIField, Interface, Interface)

    def extract(self):
        value, error = super(DateWidgetExtractor, self).extract()
        return str(value), error


# BBB
URISchemaField = URIField


class URIWidget(FieldWidget):
    grok.adapts(URIField, Interface, Interface)

    template = getTemplate('uriwidget.cpt')

    defaultHtmlClass = ['field', 'field-uri']
    defaultHtmlAttributes = set(['readonly', 'required', 'autocomplete',
                                 'maxlength', 'pattern', 'placeholder',
                                 'size', 'style'])


class URIDisplayWidget(FieldWidget):
    grok.adapts(URIField, Interface, Interface)
    grok.name('display')

    template = getTemplate('uridisplaywidget.cpt')

    @property
    def target(self):
        return self.component.target


def URISchemaFactory(schema):
    field = URIField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        minLength=schema.min_length,
        maxLength=schema.max_length,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultFactory=schema.defaultFactory,
        defaultValue=schema.default or NO_VALUE)
    return field


def register():
    registerSchemaField(URISchemaFactory, schema_interfaces.IURI)
