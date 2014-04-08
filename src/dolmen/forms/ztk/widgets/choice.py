# -*- coding: utf-8 -*-

from dolmen.forms.base.markers import NO_VALUE, Marker
from dolmen.forms.base.fields import Field
from dolmen.forms.base.widgets import FieldWidget
from dolmen.forms.base.widgets import WidgetExtractor
from dolmen.forms.ztk.fields import registerSchemaField
from dolmen.forms.ztk.interfaces import IFormSourceBinder
from dolmen.forms.ztk.widgets import getTemplate

from grokcore import component as grok
from zope import component
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import interfaces as schema_interfaces
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyTokenized, IVocabularyFactory

_ = MessageFactory("dolmen.forms.base")


class ChoiceField(Field):
    """A choice field.
    """
    _source = None
    _vocabularyFactory = None
    _vocabularyName = None

    def __init__(self, title,
                 source=None,
                 vocabularyName=None,
                 **options):
        super(ChoiceField, self).__init__(title, **options)
        if source is not None:
            self.source = source
        elif vocabularyName is not None:
            self.vocabularyFactory = vocabularyName

    @apply
    def vocabularyFactory():

        def getter(self):
            if self._vocabularyFactory is None:
                if self._vocabularyName is not None:
                    self._vocabularyFactory = component.getUtility(
                        schema_interfaces.IVocabularyFactory,
                        name=self._vocabularyName)
            return self._vocabularyFactory

        def setter(self, factory):
            if isinstance(factory, str):
                self._vocabularyName = factory
                self._vocabularyFactory = None
            else:
                self._vocabularyName = None
                self._vocabularyFactory = factory
            self._source = None

        return property(getter, setter)

    @apply
    def source():

        def getter(self):
            return self._source

        def setter(self, source):
            # Verify if this is a source or a vocabulary
            if IVocabularyTokenized.providedBy(source):
                self._source = source
            else:
                # Be sure to reset the source
                self._source = None
                self._vocabularyFactory = source

        return property(getter, setter)

    def getChoices(self, form):
        source = self.source
        if source is None:
            factory = self.vocabularyFactory
            assert factory is not None, \
                "No vocabulary source available."
            if (IContextSourceBinder.providedBy(factory) or
                IVocabularyFactory.providedBy(factory)):
                source = factory(form.context)
            elif IFormSourceBinder.providedBy(factory):
                source = factory(form)
            assert IVocabularyTokenized.providedBy(source), \
                "No valid vocabulary available, %s is not valid for %s" % (
                source, self)
        return source

    def validate(self, value, form):
        error = super(ChoiceField, self).validate(value, form)
        if error is not None:
            return error
        if not isinstance(value, Marker):
            choices = self.getChoices(form)
            if value not in choices:
                return _(u"The selected value is not among the possible choices.")
        return None

# BBB
ChoiceSchemaField = ChoiceField


class ChoiceFieldWidget(FieldWidget):
    grok.adapts(ChoiceField, Interface, Interface)
    defaultHtmlClass = ['field', 'field-choice']
    defaultHtmlAttributes = set(['required', 'size', 'style', 'disabled'])
    _choices = None

    template = getTemplate('choicefieldwidget.cpt')
    
    def __init__(self, field, form, request):
        super(ChoiceFieldWidget, self).__init__(field, form, request)
        self.source = field

    def lookupTerm(self, value):
        choices = self.choices()
        try:
            return choices.getTerm(value)
        except LookupError:
            # the stored value is invalid. fallback on the default one.
            default = self.component.getDefaultValue(self.form)
            if default is not NO_VALUE:
                return choices.getTerm(default)
        return None

    def valueToUnicode(self, value):
        term = self.lookupTerm(value)
        if term is not None:
            return term.token
        return u''

    def choices(self):
        if self._choices is not None:
            return self._choices
        # self.source is used instead of self.component in order to be
        # able to override it in subclasses.
        self._choices = self.source.getChoices(self.form)
        return self._choices


class ChoiceDisplayWidget(ChoiceFieldWidget):
    grok.name('display')

    template = getTemplate('choicedisplaywidget.cpt')
    
    def valueToUnicode(self, value):
        term = self.lookupTerm(value)
        if term is not None:
            return term.title
        return u''


class ChoiceWidgetExtractor(WidgetExtractor):
    grok.adapts(ChoiceField, Interface, Interface)

    def extract(self):
        value, error = super(ChoiceWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            choices = self.component.getChoices(self.form)
            try:
                value = choices.getTermByToken(value).value
            except LookupError:
                return (None, u'Invalid value')
        return (value, error)


# Radio Widget
class RadioFieldWidget(ChoiceFieldWidget):
    grok.adapts(ChoiceField, Interface, Interface)
    grok.name('radio')

    def renderableChoices(self):
        current = self.inputValue()
        base_id = self.htmlId()
        for i, choice in enumerate(self.choices()):
            yield {'token': choice.token,
                   'title': choice.title or choice.token,
                   'checked': choice.token == current and 'checked' or None,
                   'id': base_id + '-' + str(i)}


def ChoiceSchemaFactory(schema):
    field = ChoiceField(
        schema.title or None,
        identifier=schema.__name__,
        description=schema.description,
        required=schema.required,
        readonly=schema.readonly,
        source=schema.vocabulary or schema.source,
        vocabularyName=schema.vocabularyName,
        interface=schema.interface,
        constrainValue=schema.constraint,
        defaultFactory=schema.defaultFactory,
        defaultValue=schema.default or NO_VALUE)
    return field


def register():
    registerSchemaField(ChoiceSchemaFactory, schema_interfaces.IChoice)
