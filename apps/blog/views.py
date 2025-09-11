from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework_api.views import StandardAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, APIException
from rest_framework import permissions
import redis
from django.conf import settings

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .models import Post, Heading, PostView, PostAnalytics
from .serializers import PostListSerializer, PostSerializer, HeadingSerializer
from .utils import get_client_ip
from .tasks import increment_post_impressions
from core.permissions import HasValidAPIKey
from .tasks import increment_post_views_task


redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)

# class PostListView(ListAPIView):
#     queryset = Post.post_objects.all()
#     serializer_class = PostListSerializer


class PostListView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    # @method_decorator(cache_page(60 * 1)) # No es ideal para integrarlo con celery, es mejor con endpoints que no requieren correr logica en la funcion.
    def get(self, request):
        try:    
            cached_post = cache.get("post_list")
            if cached_post:
                for post in cached_post:
                    redis_client.incr(f"post:impressions:{post['id']}")

                return self.paginate(request, cached_post)
            
            posts = Post.post_objects.all()

            if not posts.exists():
                raise NotFound(detail='No posts found.')

            serializer = PostListSerializer(posts, many=True).data
            cache.set("post_list", serializer, timeout=60*5) # Cache por 5 minutos

            for post in posts:
                redis_client.incr(f"post:impressions:{post.id}")

        except Post.DoesNotExist:
            raise NotFound(detail='No posts found.')
        except Exception as e:
            raise APIException(detail=f"An unexpected error occurred: {str(e)}")

        return self.paginate(request, serializer)
    
    


# class PostDetailView(RetrieveAPIView):
#     queryset = Post.post_objects.all()
#     serializer_class = PostSerializer
#     lookup_field = 'slug'

class PostDetailView(StandardAPIView):
    permission_classes = [HasValidAPIKey]


    def get(self, request):
        ip_address = get_client_ip(request)

        slug = request.query_params.get('slug')
        try:

            cached_post = cache.get(f"post_detail:{slug}")
            if cached_post:
                increment_post_views_task.delay(cached_post["slug"], ip_address)
                return self.response(cached_post)

            post = Post.post_objects.get(slug=slug)

            serializer = PostSerializer(post).data

            cache.set(f"post_detail:{slug}", serializer, timeout=60 * 5)
            increment_post_views_task.delay(post.slug, ip_address)


            #Incrementar vistas en segundo plano con Celery


        except Post.DoesNotExist:
            raise NotFound(detail='The requested post does not exist.')
        
        except Exception as e:
            raise APIException(detail=f"An unexpected error occurred: {str(e)}")




        #Esto es en caso no se cree las funcionalidades desde el models.
        # client_ip = get_client_ip(request)

        # if PostView.objects.filter(post=post, ip_address=client_ip).exists():    
        #     return Response(serializer.data)
        
        # PostView.objects.create(
        #     post=post,
        #     ip_address=client_ip
        # )

        #Increment post view count = incrementa la vista
        # Ya no lo usamos ya que usaremos celery para manejar las vistas
        # try:
        #     post_analytics = PostAnalytics.objects.get(post=post)
        #     post_analytics.increment_view(request)
        # except PostAnalytics.DoesNotExist:
        #     raise NotFound(detail='Analytics data for this post does not exist.')
        # except Exception as e:
        #     raise APIException(detail=f"An error occurred while updating analytics data: {str(e)}")

     

        return self.response(serializer)


class PostHeadingsView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    def get(self, request):

        post_slug = request.query_params.get('slug')

        heading_objects = Heading.objects.filter(post__slug=post_slug)

        serialized_data = HeadingSerializer(heading_objects, many=True).data

        return  self.response(serialized_data)

    # serializer_class = HeadingSerializer

    # def get_queryset(self):
        
    #     post_slug = self.kwargs.get('slug')
    #     return Heading.objects.filter(post__slug=post_slug)

class IncrementPostClickView(StandardAPIView):
    # permission_classes = [permissions.AllowAny]
    permission_classes = [HasValidAPIKey]


    def post(self, request):
        """
        Incrementa el contador de click de un post basadi en su slug
        """

        data = request.data

        try:
           post = Post.post_objects.get(slug=data['slug'])
        except Post.DoesNotExist:
           raise NotFound(detail='The requested post does not exist.')
        
        try:
            post_analytics, created = PostAnalytics.objects.get_or_create(post=post)
            post_analytics.increment_clicks()
        except Exception as e:
            raise APIException(detail=f"An error occurred while updating post analytics: {str(e)}")

        return self.response({
            "message":"Click incremented successfully",
            "clicks":post_analytics.clicks
        })

