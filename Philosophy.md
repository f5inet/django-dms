# Goals #
This system does not intend to primarily be an out-of-the box document management system for everyone's problems. It is primarily a framework for django developers to speed up development of document managing apps. Django is about having complete control (ie perfectionists) and writing apps which are perfectly customised for the specific job they were born to perform.

# Approach #
In contrast to most other projects, the focus is on providing unobtrusive support for other developers. So, instead of providing a pre-built Document model, with all the fields and methods that I think a Document model needs, an bare abstract class is provided, which allows the developer to form it how they want it, for the problem at hand.

For example, I could decide that all document classes need a title field, summary field and a document ID. But a smaller system might want to use a SlugField instead. A Thesis model might want to call the summary an "abstract", and a UserManual field might want a foreign key to the Product it refers to.

# Other DMS projects #
I currently only know of one other document management system for Django:
  * [django-documents](http://code.google.com/p/django-documents/)
Let me know if you know of any others.