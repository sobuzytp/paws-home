from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from pets.models import Pet

from .models import AdoptionRequest

FORM = {"address": "House 1, Dhaka", "phone": "01712345678", "reason": "I love dogs",
        "previous_pet_experience": "True", "message": ""}


class AdoptionRulesTests(TestCase):
    def setUp(self):
        self.rahim = User.objects.create_user("rahim", password="pass12345!")
        self.karim = User.objects.create_user("karim", password="pass12345!")
        self.admin = User.objects.create_superuser("admin", "a@a.com", "pass12345!")
        self.max = Pet.objects.create(name="Max", animal_type="Dog", breed="Golden Retriever", age=2,
                                      gender="Male", location="Dhaka", description="Friendly")

    def test_requires_login(self):
        r = self.client.get(reverse("apply", args=[self.max.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.url)

    def test_apply_and_block_duplicate(self):
        self.client.login(username="rahim", password="pass12345!")
        self.client.post(reverse("apply", args=[self.max.pk]), FORM)
        self.assertEqual(AdoptionRequest.objects.count(), 1)
        self.client.post(reverse("apply", args=[self.max.pk]), FORM)
        self.assertEqual(AdoptionRequest.objects.count(), 1)

    def test_cannot_apply_for_adopted_pet(self):
        self.max.status = "Adopted"
        self.max.save()
        self.client.login(username="rahim", password="pass12345!")
        self.client.post(reverse("apply", args=[self.max.pk]), FORM)
        self.assertEqual(AdoptionRequest.objects.count(), 0)
        page = self.client.get(reverse("pet_detail", args=[self.max.pk]))
        self.assertContains(page, "This pet has already been adopted.")
        self.assertNotContains(page, "Apply for adoption")

    def test_approval_marks_pet_adopted_and_rejects_others(self):
        a = AdoptionRequest.objects.create(user=self.rahim, pet=self.max, phone="01712345678", address="x", reason="y")
        b = AdoptionRequest.objects.create(user=self.karim, pet=self.max, phone="01712345679", address="x", reason="y")
        a.status = "Approved"
        a.save()
        self.max.refresh_from_db(); b.refresh_from_db()
        self.assertEqual(self.max.status, "Adopted")
        self.assertEqual(b.status, "Rejected")

    def test_filters(self):
        Pet.objects.create(name="Luna", animal_type="Cat", breed="Persian", age=1, gender="Female", location="Sylhet", description="x")
        r = self.client.get(reverse("pet_list"), {"animal_type": "Dog", "gender": "Male", "location": "dhaka"})
        self.assertContains(r, "Max")
        self.assertNotContains(r, "Luna")


class ApiTests(TestCase):
    def setUp(self):
        self.rahim = User.objects.create_user("rahim", password="pass12345!")
        self.karim = User.objects.create_user("karim", password="pass12345!")
        self.admin = User.objects.create_superuser("admin", "a@a.com", "pass12345!")
        self.max = Pet.objects.create(name="Max", animal_type="Dog", breed="Golden Retriever", age=2,
                                      gender="Male", location="Dhaka", description="Friendly")
        self.c = APIClient()

    def test_pet_read_public_write_admin_only(self):
        self.assertEqual(self.c.get("/api/pets/").status_code, 200)
        data = {"name": "Z", "animal_type": "Cat", "breed": "B", "age": 1, "gender": "Male", "location": "L", "description": "d"}
        self.assertEqual(self.c.post("/api/pets/", data).status_code, 401)
        self.c.force_authenticate(self.rahim)
        self.assertEqual(self.c.post("/api/pets/", data).status_code, 403)
        self.c.force_authenticate(self.admin)
        self.assertEqual(self.c.post("/api/pets/", data).status_code, 201)

    def test_search_and_filter(self):
        self.assertEqual(self.c.get("/api/pets/?search=golden").json()["count"], 1)
        self.assertEqual(self.c.get("/api/pets/?animal_type=Dog").json()["count"], 1)
        self.assertEqual(self.c.get("/api/pets/?gender=Female").json()["count"], 0)

    def test_adoptions_only_own_and_rules(self):
        self.c.force_authenticate(self.rahim)
        r = self.c.post("/api/adoptions/", {"pet": self.max.pk, "phone": "01712345678", "address": "a", "reason": "r"})
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.json()["status"], "Pending")
        # duplicate blocked
        self.assertEqual(self.c.post("/api/adoptions/", {"pet": self.max.pk, "phone": "01712345678", "address": "a", "reason": "r"}).status_code, 400)
        # user cannot self-approve
        pk = r.json()["id"]
        self.c.put(f"/api/adoptions/{pk}/", {"phone": "01712345678", "address": "b", "reason": "r", "status": "Approved"})
        self.assertEqual(AdoptionRequest.objects.get(pk=pk).status, "Pending")
        # other user can't see it
        self.c.force_authenticate(self.karim)
        self.assertEqual(self.c.get("/api/adoptions/").json()["count"], 0)
        self.assertEqual(self.c.get(f"/api/adoptions/{pk}/").status_code, 404)
        # admin approves
        self.c.force_authenticate(self.admin)
        self.c.put(f"/api/adoptions/{pk}/", {"phone": "01712345678", "address": "b", "reason": "r", "status": "Approved"})
        self.max.refresh_from_db()
        self.assertEqual(self.max.status, "Adopted")

    def test_token_auth(self):
        reg = self.c.post("/api/register/", {"username": "newbie", "email": "n@n.com", "password": "Str0ng!pass99"})
        self.assertEqual(reg.status_code, 201)
        token = reg.json()["token"]
        c2 = APIClient(); c2.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(c2.get("/api/adoptions/").status_code, 200)
