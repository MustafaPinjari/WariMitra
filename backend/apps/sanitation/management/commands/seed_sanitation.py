from django.core.management.base import BaseCommand
from apps.sanitation.models import PublicToilet, WasteReport

class Command(BaseCommand):
    help = 'Seeds initial Wari route public toilets and waste reports data.'

    def handle(self, *args, **options):
        toilets_data = [
            {
                'name': 'Alandi Sector 1 Bio-Toilet Complex',
                'location': 'Alandi Chowk, Sector 1, Pune',
                'gender_type': 'Unisex',
                'cleanliness_score': 92,
                'is_water_available': True,
                'latitude': 18.6824,
                'longitude': 73.8973,
            },
            {
                'name': 'Camp Alpha Mobile Restroom Trailer',
                'location': 'Gate 3, Palkhi Grounds, Alandi',
                'gender_type': 'Accessible',
                'cleanliness_score': 88,
                'is_water_available': True,
                'latitude': 18.6721,
                'longitude': 73.8889,
            },
            {
                'name': 'Hadapsar Gadital Sanitation Hub',
                'location': 'Hadapsar Gadital Junction, Pune',
                'gender_type': 'Unisex',
                'cleanliness_score': 85,
                'is_water_available': True,
                'latitude': 18.5020,
                'longitude': 73.9280,
            },
            {
                'name': 'Dive Ghat Emergency Mobile Toilets',
                'location': 'Dive Ghat Slope Corridor',
                'gender_type': 'Unisex',
                'cleanliness_score': 95,
                'is_water_available': True,
                'latitude': 18.3444,
                'longitude': 74.0305,
            },
            {
                'name': 'Saswad Bus Stand Public Sanitation',
                'location': 'Near Saswad Bus Stand, Saswad',
                'gender_type': 'Unisex',
                'cleanliness_score': 78,
                'is_water_available': True,
                'latitude': 18.3450,
                'longitude': 74.0300,
            },
            {
                'name': 'Jejuri Base Public Washrooms',
                'location': 'Jejuri Temple Base Grounds',
                'gender_type': 'Female',
                'cleanliness_score': 90,
                'is_water_available': True,
                'latitude': 18.2778,
                'longitude': 74.1583,
            },
            {
                'name': 'Lonand Halt Sanitation Complex',
                'location': 'Lonand Railway Transit Ground',
                'gender_type': 'Male',
                'cleanliness_score': 82,
                'is_water_available': True,
                'latitude': 18.0417,
                'longitude': 74.1833,
            },
            {
                'name': 'Pandharpur Vitthal Temple Entry Bio-Toilets',
                'location': 'Main Vitthal Temple Entry Gate, Pandharpur',
                'gender_type': 'Accessible',
                'cleanliness_score': 96,
                'is_water_available': True,
                'latitude': 17.6775,
                'longitude': 75.3283,
            },
        ]

        waste_data = [
            {
                'location_name': 'Alandi Gate 2 Pilgrimage Path',
                'waste_type': 'Overflowing Bin',
                'description': 'Plastic bottles and paper waste overflowing near tea stalls.',
                'status': 'PENDING',
                'latitude': 18.6750,
                'longitude': 73.8920,
            },
            {
                'location_name': 'Saswad Halt Grounds Sector B',
                'waste_type': 'Plastic Waste',
                'description': 'Accumulation of disposable food packets after lunch distribution.',
                'status': 'CLEANING_DISPATCHED',
                'latitude': 18.3430,
                'longitude': 74.0290,
            },
            {
                'location_name': 'Hadapsar Vegetable Market Transit',
                'waste_type': 'Organic Waste',
                'description': 'Food remnants cleaned and disposed by municipal sanitation truck.',
                'status': 'CLEANED',
                'latitude': 18.5040,
                'longitude': 73.9260,
            },
        ]

        t_count = 0
        for data in toilets_data:
            _, created = PublicToilet.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                t_count += 1

        w_count = 0
        for data in waste_data:
            _, created = WasteReport.objects.get_or_create(
                location_name=data['location_name'],
                waste_type=data['waste_type'],
                defaults=data
            )
            if created:
                w_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {t_count} public toilets and {w_count} waste reports.')
        )
