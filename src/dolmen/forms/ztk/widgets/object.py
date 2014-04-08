# -*- coding: utf-8 -*-

from dolmen.forms.base.datamanagers import ObjectDataManager
from dolmen.forms.base.errors import Errors
from dolmen.forms.base.fields import Field, Fields
from dolmen.forms.base.components import cloneFormData
from dolmen.forms.base.markers import NO_VALUE, Marker, DEFAULT
from dolmen.forms.base.widgets import WidgetExtractor
from dolmen.forms.base.widgets import Widgets, FieldWidget
from dolmen.forms.ztk.fields import registerSchemaField
from dolmen.forms.ztk.interfaces import IObjectField
from dolmen.forms.ztk.widgets import getTemplate

from grokcore import component as grok
from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.interface import Interface, implements
from zope.schema import interfaces as schema_interfaces


class ObjectField(Field):
    """A collection field.
"""
    implements(IObjectField)
    objectFactory = DEFAULT
    dataManager = ObjectDataManager

    def __init__(self, title, schema=None, **options):
        super(ObjectField, self).__init__(title, **options)
        self._schema = schema
        self._fields = Fields()
        if schema is not None:
            self._fields.extend(schema)

    @property
    def objectSchema(self):
        return self._schema

    @property
    def objectFields(self):
        return self._fields

    def getObjectFactory(self):
        if self.objectFactory is not DEFAULT:
            return self.objectFactory
        schema = self.objectSchema
        return getUtility(IFactory, name=schema.__identifier__)

# BBB
ObjectSchemaField = ObjectField


class ObjectFieldWidget(FieldWidget):
    grok.adapts(ObjectField, Interface, Interface)

    template = getTemplate('objectfieldwidget.cpt')
    
    def prepareContentValue(self, value):
        if value is NO_VALUE:
            return {self.identifier: []}
        return {self.identifier: value}

    def update(self):
        super(ObjectFieldWidget, self).update()
        value = self.component.dataManager(self.inputValue())
        form = cloneFormData(self.form, value, self.identifier)
        self.objectWidgets = Widgets(form=form, request=self.request)
        self.objectWidgets.extend(self.component.objectFields)
        self.objectWidgets.update()


class ObjectDisplayWidget(ObjectFieldWidget):
    grok.name('display')


class ObjectFieldExtractor(WidgetExtractor):
    grok.adapts(ObjectField, Interface, Interface)

    def extract(self):
        is_present = self.request.form.get(self.identifier, NO_VALUE)
        if is_present is NO_VALUE:
            return (NO_VALUE, None)
        value = None
        form = cloneFormData(self.form, None, self.identifier)
        data, errors = form.extractData(self.component.objectFields)
        if not errors:
            factory = self.component.getObjectFactory()
            # Create an object with values
            value = factory(**dict(filter(
                        lambda (k, v): not isinstance(v, Marker),
                        data.items())))
            return (value, None)
        return (value, Errors(*errors, identifier=self.identifier))


def ObjectSchemaFactory(schema):
    field = ObjectField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        schema=schema.schema,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultFactory=schema.defaultFactory,
        defaultValue=schema.default or NO_VALUE)
    return field


def register():
    registerSchemaField(ObjectSchemaFactory, schema_interfaces.IObject)
