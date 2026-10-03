# Pet Adoption & Rescue Platform

A Django web application where users browse pets, apply to adopt them, and track their requests.
Admins manage everything through Django Admin. Includes a REST API built with Django REST Framework.

## Features

**Website (Django templates + Bootstrap 5)**
- Register, login, logout, profile page
- Pet list with cards, search/filter (name, animal type, breed, gender, location, status) and pagination
- Pet details page (adoption button hidden for adopted pets)
- Adoption application form and "My adoption requests" dashboard
- Success / error messages, responsive layout, navigation bar

**Business rules**
1. Only `Available` pets can receive new applications.
2. One user cannot have more than one active (Pending/Approved) request for the same pet. This is enforced in the model `clean()` and by a conditional database `UniqueConstraint`.
3. When an admin approves a request, the pet becomes `Adopted` and the other pending requests for that pet are automatically set to `Rejected`. New applications are blocked.

**Django Admin**
- Pets: add, edit, delete, upload image, change status (editable directly in the list)
- Adoption requests: user, pet, date, phone, reason, status. Change status in the list, or use the bulk actions "Approve" / "Reject".

**REST API (DRF)**
| Endpoint | Methods | Access |
|---|---|---|
| `/api/pets/` | GET, POST | read: everyone, write: admin only |
| `/api/pets/<id>/` | GET, PUT, PATCH, DELETE | read: everyone, write: admin only |
| `/api/adoptions/` | GET, POST | logged-in users (own requests only) |
| `/api/adoptions/<id>/` | GET, PUT, PATCH | owner (admins can see all and change `status`) |
| `/api/register/` | POST | create user and receive a token |
| `/api/token/` | POST | username + password, receive a token |

Search and filters: `/api/pets/?search=golden`, `/api/pets/?animal_type=Dog`, `/api/pets/?gender=Male`,
`/api/pets/?location=dhaka`, `/api/pets/?status=Available`. Pagination: `/api/pets/?page=2`.
Authentication: Token (`Authorization: Token <key>`) or session.

**Bonus features done:** favorite pets, website pagination, API pagination, token authentication, pet categories (Dog, Cat, Bird, Rabbit, Other).

## Setup

```bash
git clone https://github.com/sobuzytp/paws-home.git
cd paws-home/pet_adoption_platform

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_pets        # optional: adds 8 sample pets
python manage.py runserver
```

- Website: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API root: http://127.0.0.1:8000/api/

Run tests: `python manage.py test`

## API examples

```bash
# get a token
curl -X POST http://127.0.0.1:8000/api/token/ -d "username=rahim&password=yourpassword"

# list available dogs
curl "http://127.0.0.1:8000/api/pets/?animal_type=Dog&status=Available"

# apply to adopt pet 1
curl -X POST http://127.0.0.1:8000/api/adoptions/ \
  -H "Authorization: Token <your-token>" \
  -d "pet=1&phone=01712345678&address=Dhaka&reason=I love dogs&previous_pet_experience=true"
```

## Project structure

```
config/      settings and root urls
accounts/    register, login, logout, profile
pets/        Pet and Favorite models, list/detail views, seed_pets command
adoptions/   AdoptionRequest model, apply form, dashboard, admin actions
api/         DRF serializers, viewsets, urls
templates/   all HTML templates
static/      CSS
```
