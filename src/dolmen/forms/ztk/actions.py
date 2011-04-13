# -*- coding: utf-8 -*-

from dolmen.forms.base import Action, _
from dolmen.forms.base.markers import NO_VALUE, NO_CHANGE, SUCCESS, FAILURE
from dolmen.forms.base.datamanagers import ObjectDataManager
from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent


class CancelAction(Action):
    """Cancel the current form and return on the default content view.
    """

    def __call__(self, form):
        form.redirect(form.url())


_marker = object()

class EditAction(Action):
    """Edit the form content using the form fields.
    """

    def applyData(self, form, content, data):
        for field in form.fields:
            value = data.get(field.identifier, _marker)
            if value is NO_VALUE and not field.required:
                value = data.getDefault(field, _marker)
            if value is not _marker and value is not NO_CHANGE:
                content.set(field.identifier, value)

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return FAILURE

        content = form.getContentData()
        self.applyData(form, content, data)
        notify(ObjectModifiedEvent(content.content))
        form.status = _(u"Modification saved.")
        return SUCCESS


class AddAction(EditAction):
    """Add a new content in the form content, saving the form fields
    on the newly created content.
    """
    fieldName = 'title'

    def __init__(self, title, factory):
        super(AddAction, self).__init__(title)
        self.factory = factory

    def create(self, form, data):
        content = self.factory()
        self.applyData(form, ObjectDataManager(content), data)
        notify(ObjectCreatedEvent(content))
        return content

    def chooseName(self, container, content, name):
        raise NotImplementedError

    def add(self, form, content, data):
        container = form.getContent()
        default_name = None
        if self.fieldName is not None:
            default_name = getattr(content, self.fieldName)

        name = self.chooseName(container, content, default_name)
        container[name] = content

    def nextURL(self, form, content):
        return form.url(content)

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return FAILURE

        content = self.create(form, data)
        self.add(form, content, data)
        form.redirect(self.nextURL(form, content))
        return SUCCESS
