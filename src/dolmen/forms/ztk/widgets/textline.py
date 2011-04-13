# Text line widget

from grokcore import component as grok
from dolmen.forms.ztk.widgets import getTemplate
from dolmen.forms.ztk.fields import (
    SchemaField, SchemaFieldWidget, registerSchemaField)
from zope.schema import interfaces as schema_interfaces


def register():
    registerSchemaField(TextLineSchemaField, schema_interfaces.ITextLine)


class TextLineSchemaField(SchemaField):
    """A text line field.
    """


class TextLineWidget(SchemaFieldWidget):
    grok.adapts(TextLineSchemaField, None, None)
    template = getTemplate('textlinewidget.pt')
