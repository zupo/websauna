"""CRUD based on SQLAlchemy and Deform."""
from abc import abstractmethod
from pyramid_web20.utils import traverse

class CRUD:
    """Define create-read-update-delete inferface for an model.

    We use Pyramid traversing to get automatic ACL permission support for operations. As long given CRUD resource parts define __acl__ attribute, permissions are respected automatically.

    URLs are the following:

        List: $base/listing

        Add: $parent/add

        View: $parent/$id

        Edit: $parent/$id/edit

        Delete: $parent/$id/delete
    """

    # How the model is referred in templates. e.g. "User"
    friendly_name = "xx"

    #: Factory for creating $base/id traversing parts. Maps to the show object.
    instance = None

    #: Listing object presenting $base/listing traversing part. Maps to show view
    listing = None

    show = None
    add = None
    edit = None
    delete = None

    def __init__(self):

        # TODO: currently it is not possible to share CRUD parts among the classe. Create factory methods which can be called in the case we want to use the same Listing() across several CRUDs, etc.

        traverse.make_lineage(self, self.listing, "listing")
        traverse.make_lineage(self, self.add, "add")

    def get_model(self):
        pass

    def make_instance(self, obj):
        # Wrap object to a traversable part
        instance = self.instance(obj)
        traverse.make_lineage(self, instance, instance.get_id())
        return instance

    def traverse_to_object(self, id):
        """Wraps object to a traversable URL.

        Loads raw database object with id and puts it inside ``Instance`` object,
         with ``__parent__`` and ``__name__`` pointers.
        """
        obj = self.fetch_object(id)
        return self.make_instance(obj)


    def __getitem__(self, id):
        if id == "listing":
            return self.listing
        elif id == "add":
            return self.add
        else:
            return self.traverse_to_object(id)


    @abstractmethod
    def fetch_object(self, id):
        """Load object from the database for CRUD path for view/edit/delete."""
        raise NotImplementedError("Please use concrete subclass like pyramid_web20.syste.crud.sqlalchemy")


class CRUDResourcePart:
    """A resource part of CRUD traversing."""

    template = None

    def get_crud(self):
        return self.__parent__

    def get_model(self):
        return self.__parent__.get_model()


class Instance:
    """An object for view, edit, delete screen."""

    template = "crud/show.html"

    def __init__(self, obj):
        self.obj = obj

    @abstractmethod
    def get_id(self):
        """Extract id from the self.obj for traversing."""
        raise NotImplementedError()

    def get_model(self):
        return self.__parent__.get_model()

    def get_title(self):
        """Title used on view, edit, delete, pages."""
        return self.get_id()


class Column:
    """Define listing in a column. """

    header_template = "crud/column_header.html"

    body_template = "crud/column_body.html"

    def __init__(self, id, name=None, renderer=None, header_template=None, body_template=None):
        """
        :param id: Must match field id on the model
        :param name:
        :param renderer:
        :param header_template:
        :param body_template:
        :return:
        """
        self.id = id
        self.name = name
        self.renderer = renderer

        if header_template:
            self.header_template = header_template

        if body_template:
            self.body_template = body_template

    def get_value(self, obj):
        """Extract value from the object for this column.

        Called in listing body.
        """
        return getattr(obj, self.id)


class ControlsColumn(Column):
    """Render View / Edit / Delete buttons."""
    def __init__(self, id="controls", name="View / Edit", header_template="crud/column_header_controls.html", body_template="crud/column_body_controls.html"):
        super(ControlsColumn, self).__init__(id=id, name=name, header_template=header_template, body_template=body_template)


class CRUDObjectPart:
    """A resource part of CRUD traversing."""

    template = None

    def get_model(self):
        return self.__parent__.get_model()

    def __getitem__(self, item):
        pass


class Listing(CRUDResourcePart):
    """Describe mappings to a CRUD listing view."""

    #: In which frame we embed the listing. The base template must defined {% block crud_content %}
    base_template = None

    def __init__(self, title=None, columns=[], template=None, base_template=None):
        self.title = title
        self.columns = columns

        if template:
            self.template = template

        if base_template:
            self.base_template = base_template

    @abstractmethod
    def get_count(self):
        """Get count of total items of this mode."""
        raise NotImplementedError("Please use concrete subclass like pyramid_web20.syste.crud.sqlalchemy.Listing")

    @abstractmethod
    def get_batch(self, start, end):
        """Get batch of items from start to end."""
        raise NotImplementedError("Please use concrete subclass like pyramid_web20.syste.crud.sqlalchemy.Listing")

    def get_instance(self, obj):
        return self.get_crud().make_instance(obj)


class Show:
    """View the item."""

    def __init__(self, includes=None):
        """
        :param includes ``includes`` hint for ``colanderalchemy.SQLAlchemySchemaNode``
        """
        self.includes = includes

