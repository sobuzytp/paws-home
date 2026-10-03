from django.core.management.base import BaseCommand

from pets.models import Pet

SAMPLE = [
    ("Max", "Dog", "Golden Retriever", 2, "Male", "Dhaka", "Max is friendly and playful. He loves fetch and gets along with kids."),
    ("Luna", "Cat", "Persian", 1, "Female", "Chattogram", "Luna is calm and cuddly, and loves sunny window spots."),
    ("Coco", "Dog", "Labrador", 3, "Female", "Dhaka", "Coco is gentle, house-trained and great with other dogs."),
    ("Bella", "Rabbit", "Holland Lop", 1, "Female", "Sylhet", "Bella is shy at first, but very sweet once she trusts you."),
    ("Kiwi", "Bird", "Cockatiel", 2, "Male", "Dhaka", "Kiwi whistles tunes and likes company."),
    ("Rocky", "Dog", "German Shepherd", 4, "Male", "Khulna", "Rocky is loyal, smart and needs an active home."),
    ("Milo", "Cat", "Siamese", 2, "Male", "Dhaka", "Milo is talkative, curious and very affectionate."),
    ("Daisy", "Dog", "Beagle", 5, "Female", "Rajshahi", "Daisy is a calm senior who just wants a warm lap."),
]


class Command(BaseCommand):
    help = "Create sample pets for demo purposes."

    def handle(self, *args, **options):
        created = 0
        for name, typ, breed, age, gender, loc, desc in SAMPLE:
            _, was_created = Pet.objects.get_or_create(
                name=name, breed=breed,
                defaults=dict(animal_type=typ, age=age, gender=gender, location=loc, description=desc),
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f"{created} sample pets created."))
