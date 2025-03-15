
from django.db.models import Q

from vault.models.document import Document


from helper.utils.response.pagination import PaginatorCustom




class DocumentManager:

    @staticmethod
    def retrieve_documents(user,**kwargs):
        request = kwargs.get("request")


        dynamic_filters = Q()

        queryset = Document.objects.filter(dynamic_filters)
        page_size = kwargs.get('request').GET.get('page_size', 10)
        paginator = PaginatorCustom(
            queryset, kwargs.get('request'),
            serialize_func=Document.get_serialized_data
        )
        return paginator.paginate(page_size)


