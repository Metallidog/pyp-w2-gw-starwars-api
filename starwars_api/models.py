from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.mk
        """

        for key, value in json_data.items():
            setattr(self, key, value)
            
        
    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        qs_dict = {'people':api_client.get_people, 'films':api_client.get_films}
        return cls(qs_dict[cls.RESOURCE_NAME](resource_id))
        

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        cls_str = cls.RESOURCE_NAME.title() + "QuerySet"
        return globals()[cls_str]()

      
class People(BaseModel):
    """Representing a single person"""
    
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.id = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        qs_dict = {'people':api_client.get_people, 'films':api_client.get_films}
        
        while self.id < self.count():
            self.id += 1
            self.objects = qs_dict[self.RESOURCE_NAME](self.id)
            return globals()[self.RESOURCE_NAME.title()](self.objects)
        
        raise StopIteration()
        

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        method = 'get_{}'.format(self.RESOURCE_NAME)
        data = getattr(api_client, method)()
        return data['count']


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()
        
    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
