Django-dms provides a document management system and a framework to integrate customised document storage with django projects.

This how-to will go through the following:
  * Seeing what django-dms can do (using the test projects)
  * Using the sample DMS apps
  * Using the DMS framework

# Requirements #
  * Python 2.5+ (for now)
  * Django 1.1 (currently unreleased, use the SVN version).
  * sorl.thumbnail (optional, if you want thumbnails and previews)

I haven't decided whether or not to support django 1.0. There are some nice features coming up in Django 1.1 which I would like to make use of, otherwise it'll be a little bit of work, and there is often no need to use django 1.0 for brand new projects. If you really want this, let me know and I'll put something together :-)

# Seeing what django-dms can do #
Two test projects are provided (with data) to demonstrate django-dms in action. They work out-of-the-box with no setup required. Start the test server as follows:
```
cd trunk/tests/small_dms/
python ./manage.py syncdb --noinput
python ./manage.py runserver
```
An admin user is created with username/password set to admin/admin. It would be best if you had django and sorl.thumbnail installed in your pythonpath :-)

# Using the sample DMS apps #
The sample apps can be found here:
  * `django_dms.apps.small_dms`: for fewer documents, friendly
  * `django_dms.apps.large_dms`: for many documents, scalable
To use them, add the relevant app to INSTALLED\_APPS and add an entry to the project's `urls.py` such as
```
urlpatterns = patterns('',
    (r'^documents', include('django_dms.apps.small_dms.urls')),
)
```
The apps are designed to use the same templates for the rest of your site, provided you have followed some standard django conventions:
  * Base template is called `base.py`
  * Base template provides the following blocks: `content`, `body_class` and `extra_head`
  * NB These can be overriden by overriding the templates under `small_dms`/`large_dms` templates.
If you want to take advantage of some of the javascript in the apps, you will need to provide jquery and jquery.lightbox. See the test projects and templates for more details.

The two sample apps are used in the two test projects provided (`trunk/tests` in the repository), they should start up out-of-the-box with a simple `./manage.py syncdb --noinput` and `./manage.py runserver`. Have a look at those if you are having trouble using any of the apps.
# Using the DMS framework #
`django-dms` can be used as a framework, that is, to help developers build apps with document management features. It provides the following features:
  * abstract model class "`DocumentBase`"
  * [automatic data population using file's metadata](MetadataExtraction.md)
  * [generic views](GenericViews.md) (list, detail, upload)
  * [document delivery](GenericViews.md) (thumbnail preview, in-browser view, download, email)
  * [upload by email](EmailUpload.md) (and populate other fields using subject/body/sender/date)
  * custom model fields: UUID, FriendlyDocID
Two out-of-the-box document management systems are also provided as an example, for non-developers and for internal testing.
  * Basic DMS for a small database (using slug references)
  * Basic DMS for a larger database (using FriendlyDocID references)

## Using the `DocumentBase` model ##
In your `models.py`, simply create a model from either `DocumentBase` or `BasicDocumentBase`.
```
from django_dms import DocumentBase

class Thesis(DocumentBase):
    title    = models.CharField(max_length=150)
    author   = models.CharField(max_length=150)
    abstract = models.TextField()
    grade    = models.CharField(max_length=2)
```

The Thesis class now has a few additional fields:
  * `uuid`: a universal id, used as the internal filename
  * `file`: the file in question
  * `file_mimetype`: the content type or mimetype of the file
  * `file_extension`: the original extension, used for delivery filename
  * `date_updated`: date this document was updated
  * `date_added`: date this document was added to the system
It also has the following methods/attributes/properties defined, which can be overridden:
  * `file_friendly_filename`: used for the delivery filename
  * `file_thumbnail_small`: a link to a small thumbnail (about 200px)
  * `file_thumbnail_medium`: a link to a medium thumbnail (about 600px)
  * `file_already(mode, request)`: whether or not the user has already viewed/downloaded/sent this document