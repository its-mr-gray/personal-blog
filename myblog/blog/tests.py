from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Post

# Create your tests here.


class PostAPITestCase(APITestCase):
    def setUp(self):
        self.post = Post.objects.create(
            post_title="test post",
            post_content="howdy howdy howdy",
            author_name="test guy",
            created_date="08-29-2004",
        )

    def test_create_post(self):
        url = reverse("post-list")
        data = {
            "post_title": "scoobert",
            "post_content": "doobert",
            "author_name": "steve jobs",
            "created_date": "01-01-2000",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_get_post_list(self):
        url = reverse("post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("test post", str(response.data))

    def test_get_post_details(self):
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["post_title"], self.post.post_title)
