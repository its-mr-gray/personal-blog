from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Post

# Create your tests here.


class PostAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.post = Post.objects.create(
            post_title="test post",
            post_content="howdy howdy howdy",
            author=self.user,
            created_date="2004-08-24",
        )

    def test_create_post(self):
        url = reverse("post-list")
        data = {
            "post_title": "scoobert",
            "post_content": "doobert",
            "created_date": "2000-01-01",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_get_post_list(self):
        self.client.logout()
        url = reverse("post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("test post", str(response.data))

    def test_get_post_details(self):
        self.client.logout()
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["post_title"], self.post.post_title)

    def test_delete_post(self):
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_update_post(self):
        url = reverse("post-detail", args=[self.post.id])
        data = {
            "post_title": "skibby",
            "post_content": self.post.post_content,
            "created_date": str(self.post.created_date),
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.post_title, "skibby")

    def test_nonexistant_post(self):
        url = reverse("post-detail", args=[87405982734098257034987502983745])
        get_response = self.client.get(url)
        delete_response = self.client.delete(url)
        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)

    def test_invalid_field(self):
        url = reverse("post-list")
        data = {
            "post_title": "",
            "post_content": "doobert",
            "created_date": "2000-01-01",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("post_title", response.data)

    def test_missing_field(self):
        url = reverse("post-list")
        data = {
            "post_content": "howdy",
            "created_date": "2000-01-01",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("post_title", response.data)

    def test_unauth_cannot_create_post(self):
        self.client.logout()
        url = reverse("post-list")
        data = {
            "post_title": "scoobert",
            "post_content": "doobert",
            "created_date": "2000-01-01",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_unaut_cannot_update_post(self):
        self.client.logout()
        url = reverse("post-detail", args=[self.post.id])
        data = {
            "post_title": "skibby",
            "post_content": self.post.post_content,
            "created_date": str(self.post.created_date),
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_unauth_cannot_delete_post(self):
        self.client.logout()
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)


class PostOwnershipTest(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            username="user_a", password="user_a_pass"
        )
        self.user_b = User.objects.create_user(
            username="user_b", password="user_b_password"
        )
        self.post = Post.objects.create(
            post_title="test post",
            post_content="howdy howdy howdy",
            author=self.user_a,
            created_date="2004-08-24",
        )
        self.detail_url = reverse("post-detail", args=[self.post.id])

    def test_owner_can_update(self):
        self.client.login(username="user_a", password="user_a_pass")
        response = self.client.put(
            self.detail_url,
            {
                "post_title": "updated",
                "post_content": "stinky",
                "created_date": "2000-08-30",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_owner_can_delete(self):
        self.client.login(username="user_a", password="user_a_pass")
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)

    def test_non_owner_cannot_update(self):
        self.client.login(username="user_b", password="user_b_pass")
        response = self.client.put(
            self.detail_url,
            {
                "post_title": "skeedly deedly",
                "post_content": "ya mum",
                "created_date": "2003-09-23",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_non_owner_cannot_delete(self):
        self.client.login(username="user_b", password="user_b_pass")
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 403)


class PostFilteringTest(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create(username="tim", password="tim_pass")
        self.user_b = User.objects.create(username="alice", password="alice_pass")
        Post.objects.create(
            post_title="Test1",
            post_content="just a test",
            author=self.user_a,
            created_date="2022-01-01",
        )
        Post.objects.create(
            post_title="SomethingElse",
            post_content="a second test",
            author=self.user_b,
            created_date="2009-09-09",
        )
        Post.objects.create(
            post_title="Test3",
            post_content="a third test",
            author=self.user_a,
            created_date="2010-09-26",
        )

    def test_filter_by_post(self):
        url = reverse("post-list") + "?post_title=Test"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            all("Test" in post["post_title"] for post in response.data["results"])
        )

    def test_filter_by_author(self):
        url = reverse("post-list") + f"?author__username={self.user_a.username}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            all(
                post["author"] == self.user_a.username
                for post in response.data["results"]
            )
        )

    def test_filter_by_date(self):
        url = reverse("post-list") + "?created_date=2010-09-26"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            all(
                post["created_date"] == "2010-09-26"
                for post in response.data["results"]
            )
        )

    def test_combined_filters(self):
        url = reverse("post-list") + f"?post_title=Test&author__={self.user_a.username}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            all(
                "Test" in post["post_title"] and post["author"] == self.user_a.username
                for post in response.data["results"]
            )
        )

    def test_no_matches(self):
        url = reverse("post-list") + "?post_title=AMadeUpTitle"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)


class PostUserAuthenticationTest(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create(username="tim", password="tim_pass")
        self.user_b = User.objects.create(username="alice", password="alice_pass")

    def test_user_can_register(self):
        url = reverse("user-register")
        response = self.client.get(url, self.user_a)
        self.assertEqual(response.status_code, 201)
