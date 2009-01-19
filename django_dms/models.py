#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: DMS framework models
    Project: django_dms
     Author: Will Hardy
       Date: November 2008
  $Revision$
"""

import os
import uuid
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.encoding import force_unicode, smart_unicode

from django_dms.utils import ChoicesBank, Choices, UUIDField, HashField, get_hash
from mimetypes import guess_type

def get_filename_from_uuid(instance, filename):
    populate_file_extension_and_mimetype(instance, filename)
    stem, extension = os.path.splitext(filename)
    return 'documents/%s%s' % (instance.uuid, extension)

def populate_file_extension_and_mimetype(instance, filename):
    # First populate the file extension and mimetype
    instance.file_mimetype, encoding = guess_type(filename) or ""
    slug, instance.file_extension = os.path.splitext(filename)
    #instance.slug, instance.extension = os.path.splitext(filename)

class DocumentBase(models.Model):
    """ Minimum fields for a document entry.
        Inherit this model to customise document metadata, see BasicDocument for an example.
    """
    uuid           = models.CharField(max_length=36, default=lambda:unicode(uuid.uuid4()), blank=True, editable=False, primary_key=True)
    # TODO: The django admin uses the file extension to determine the filetype for the preview
    # A new widget will have to be created, in a similar fashion to the automatic one
    file           = models.FileField(upload_to=get_filename_from_uuid)#lambda i,f: 'documents/%s' % i.uuid)
    file_mimetype  = models.CharField(max_length=50, default="", editable=False)
    file_extension = models.CharField(max_length=10, default="", editable=False)

    date_added   = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save_file(self, contents, save=False):
        " Save a file, creating a new document_version if necessary. "
        self.file.save(contents.name, contents, save=save)
        # This is now done elsewhere
        #self.file_mimetype = guess_type(contents.name) or ""
        #try:
            #self.file_extension = contents[contents.rindex(".")+1:] or ""
        #except ValueError:
            #pass
        #self.save()

    def __unicode__(self):
        return self.uuid

    @property
    def friendly_filename(self):
        """ A friendly filename (ie not the UUID) for the user to see when they download.
            Overload this with eg a slug field. 
        """
        return 'untitled.%s' % self.file_extension


    def already(self, mode, request):
        """ Tests if a user has already viewed, downloaded or sent this document. 
            Assumes this model has a log of document interactions.
        """
        mode = getattr(DocumentInteractionBase.MODES, mode.upper())

        if request.user.is_anonymous():
            return bool(self.interactions.filter(mode=mode, session_key=request.session.session_key))
        else:
            return bool(self.interactions.filter(mode=mode, user=request.user))


class BasicDocumentBase(DocumentBase):
    """ Basic document entry, with a selected metadata.
    """
    title        = models.CharField(max_length=150, default="", blank=True)
    slug         = models.SlugField() # Make this unique for smaller databases
    summary      = models.TextField(default="", blank=True)
    author       = models.CharField(max_length=150, default="", blank=True)
    date_created = models.DateTimeField(null=True, blank=True)

    # NB: Automate this in the form
    uploaded_by  = models.ForeignKey(User, null=True, blank=True, editable=False)

    # Extract plaintext from document and store in database to allow full-text searching
    plaintext    = models.TextField(default="", blank=True, editable=False)

    def __unicode__(self):
        return self.title or 'untitled (%s...%s)' % (self.uuid[:3], self.uuid[-3:])

    class Meta:
        abstract = True

    @property
    def friendly_filename(self):
        """ A friendly filename (ie not the UUID) for the user to see when they download.
            Overload this with a slug field. 
        """
        return '%s.%s' % ('_'.join(self.slug.split()), self.file_extension)

    # METADATA handling fields

    AUTO_METADATA = dict(title='title', file_mimetype='mimetype', author='creator', date_created='creation date')
    def process_metadata_title(self, value):
        return value.isupper() and value.title() or value
    def process_metadata_date_created(self, value):
        # TODO: This should be in the metadata engine
        for pattern in ('%Y-%m-%dT%H:%M:%SZ', '%Y%m%d%H%M%S'):
            try:
                # String is trimmed to the size of pattern, assuming that
                # it is the same length as the string it is matching (coincidently, it often is!).
                return datetime.strptime(value[:len(pattern)], pattern)
            except ValueError:
                continue
        return value


class DocumentInteractionBase(models.Model):
    MODES = Choices('Viewed', 'Downloaded', 'Sent')

    #document    = models.ForeignKey(Document, related_name="interactions")
    mode        = models.PositiveSmallIntegerField(choices=MODES)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    user        = models.ForeignKey(User, null=True, blank=True)
    timestamp   = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return u'%s %s by %s on %s' % (self.document, self.get_mode_display().lower(), 
                                        self.user or self.session_key, self.timestamp.date())

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            # Set the mode automatically, based on which class is saving this object.
            self.mode = self.__class__.MODE
        except AttributeError:
            pass
        super(DocumentInteractionBase, self).save(*args, **kwargs)

#def interaction_model_factory(document_model):
    #""" Create a class that will correctly implement document interactions. """
    ## TODO: This is not the best approach, because the class name is not explicitly determined by the user.
    ## TODO: Is there a way of using the user's chosen name for this?
    ## TODO: register this class and any subclasses?
    #class DocumentInteraction(DocumentInteractionBase):
        #document    = models.ForeignKey(document_model, related_name="interactions")
    #return DocumentInteraction