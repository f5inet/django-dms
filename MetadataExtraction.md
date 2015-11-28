## Basic use ##
Metadata contained within a file can be used to automatically populate attributes in your model. This makes use of the [libextractor](http://www.gnu.org/software/libextractor/) library, which needs to be installed with python bindings.

If you connect the `extract_metadata` function, data can be automatically
extracted from the uploaded file on save.
```
class Report(DocumentBase):
    name = models.CharField(max_length=150)

from django_dms import metadata
metadata.register(Report)

```

You can also choose which fields get imported, the following example populates report.name from any 'title' field from the document's metadata.
```
class Report(DocumentBase):
    name = models.CharField(max_length=150)
    
from django_dms import metadata
metadata.register(Report, name='title')
```