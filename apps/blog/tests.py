from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient
from django.core.cache import cache


from .models import Category, Post, PostAnalytics, Heading
# Create your tests here.

#Models Test
class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Tech",
            title="Technology",
            description="All about technology",
            slug="tech"
        )

    def test_category_creation(self):
        self.assertEqual(str(self.category), "Tech")
        self.assertEqual(self.category.title, "Technology")
        self.assertEqual(self.category.description, "All about technology")
        self.assertEqual(self.category.slug, "tech")

class PostModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Tech",
            title="Technology",
            description="All about technology",
            slug="tech"
        )
        self.post = Post.objects.create(
            title="Post 1",
            description="A test post",
            content="Content for the test post",
            thumbnail=None,
            keywords="test, post",
            slug="post-1",
            category=self.category,
            status="published"
        )

    def test_post_creation(self):
        self.assertEqual(str(self.post), "Post 1")
        self.assertEqual(self.post.category.name, "Tech")
    
    def test_post_published_manager(self):
        self.assertTrue(Post.post_objects.filter(status="published").exists())

class PostAnalyticsModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Analytics",
            slug="analytics"
        )
        self.post = Post.objects.create(
            title="Analytics post",
            description="Post for analytics",
            content="Analytics content",
            slug="analytics-post",
            category=self.category,
        )
        self.analytics, _ = PostAnalytics.objects.get_or_create(post=self.post)

    def test_click_through_rate_update(self):
        self.analytics.increment_impressions()
        self.analytics.increment_clicks()
        self.analytics.refresh_from_db()
        self.assertEqual(self.analytics.click_through_rate, 100.0)

class HeadingModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Headings",
            slug="headings"
        )
        self.post = Post.objects.create(
            title="Heading post",
            description="Post with headings",
            content="Content with headings",
            slug="heading-post",
            category=self.category,
        )
        self.heading = Heading.objects.create(
            post=self.post,
            title="Heading 1",
            slug="heading-1",
            level=1,
            order=1
        )

    def test_heading_creation(self):
        self.assertEqual(self.heading.slug, "heading-1")
        self.assertEqual(self.heading.level, 1)

#Views Test
class PostListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.category = Category.objects.create(
            name="Api",
            slug="api"
        )
        self.api_key = settings.VALID_API_KEYS[0]
        self.post = Post.objects.create(
            title="API Post",
            description="Post for API testing",
            content="API content",
            slug="api-post",
            category=self.category,
            status="published"
        )

    def test_get_post_list(self):
        url = reverse('post-list')
        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key
        )

        data = response.json()

        self.assertIn("success", data)
        self.assertTrue(data["success"])
        self.assertIn("status", data)
        self.assertEqual(data["status"], 200)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 1)

        results = data["results"]
        self.assertEqual(len(results), 1)

        post_data = results[0]
        self.assertEqual(post_data["title"], "API Post")
        self.assertEqual(post_data["slug"], self.post.slug)
        self.assertEqual(post_data["category"]["name"], "Api")
        
class PostDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()

        self.api_key = settings.VALID_API_KEYS[0]
        self.category = Category.objects.create(
            name="Detail",
            slug="detail"
        )
        self.post = Post.objects.create(
            title="Detail Post",
            description="Post for detail view testing",
            content="Detail content",
            slug="detail-post",
            category=self.category,
            status="published"
        )
    
    @patch('apps.blog.views.increment_post_views_task.delay')
    def test_get_post_detail_success(self, mock_increment_views):
        """
            Test para verificar que se obtienen los detalles de un post correctamente
            y que la vista se incrementa en segundo plano usando Celery.
        """
        #Ruta hacia la vista con query params "slug"
        url = reverse('post-detail') + f'?slug={self.post.slug}'

        #Simular una solicitud GET a la vista con encabezado de API key
        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key
        )

        #Verificar la respuesta
        self.assertEqual(response.status_code, 200)

        #Decodificar la respuesta JSON
        data = response.json()

        #Verifica el formato y contenido de la respuesta
        self.assertIn("success", data)
        self.assertTrue(data["success"])
        self.assertIn("status", data)
        self.assertEqual(data["status"], 200)
        self.assertIn("results", data)

        post_data = data["results"]

        self.assertEqual(post_data["title"], "Detail Post")
        self.assertEqual(post_data["slug"], self.post.slug)
        self.assertEqual(post_data["category"]["name"], "Detail")

        mock_increment_views.assert_called_once_with(self.post.slug, '127.0.0.1')

       
