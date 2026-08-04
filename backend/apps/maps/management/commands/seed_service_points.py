from django.core.management.base import BaseCommand
from apps.maps.models import ServicePoint

class Command(BaseCommand):
    help = 'Seeds initial Wari route service points on the interactive map.'

    def handle(self, *args, **options):
        initial_points = [
            {
                'name': 'Drinking Water Point 4 (Alandi Chowk)',
                'category': 'Water',
                'details': 'Continuous clean drinking water tanker with 10 taps and ORS distribution.',
                'latitude': 18.6824,
                'longitude': 73.8973,
                'address': 'Alandi Chowk, Sector 1, Pune',
                'contact_number': '+91 98230 11223',
                'status': 'Active',
                'capacity_info': '50,000L Capacity • Available 24x7',
            },
            {
                'name': 'Camp Alpha Primary Health Center',
                'category': 'Medical',
                'details': 'Primary medical triage, emergency first aid, heat stroke treatment, and free medicines.',
                'latitude': 18.6721,
                'longitude': 73.8889,
                'address': 'Gate 3, Palkhi Transit Grounds, Alandi',
                'contact_number': '+91 98221 44556',
                'status': 'Active',
                'capacity_info': '4 Doctors • 12 Beds • 2 Ambulances',
            },
            {
                'name': 'Saswad Annadhana & Food Camp',
                'category': 'Food',
                'details': 'Free hot Maharashtrian meals (Pithla Bhakri, Khichdi, Tea) served continuously.',
                'latitude': 18.3450,
                'longitude': 74.0300,
                'address': 'Near Saswad Bus Stand, Saswad',
                'contact_number': '+91 99700 88990',
                'status': 'Available',
                'capacity_info': 'Serves ~15,000 pilgrims/day',
            },
            {
                'name': 'Dive Ghat Emergency First Aid & Ambulance Post',
                'category': 'Medical',
                'details': 'Critical medical station for steep slope corridor emergency response.',
                'latitude': 18.3444,
                'longitude': 74.0305,
                'address': 'Dive Ghat Slope Point, Pune-Saswad Highway',
                'contact_number': '+91 98234 56789',
                'status': 'Active',
                'capacity_info': '15 Triage Beds • ICU Ambulance on Standby',
            },
            {
                'name': 'Hadapsar Public Sanitation Complex',
                'category': 'Toilets',
                'details': 'Clean eco-friendly mobile bio-toilets with continuous water supply and wash stations.',
                'latitude': 18.5020,
                'longitude': 73.9280,
                'address': 'Hadapsar Gadital, Pune',
                'contact_number': '+91 98900 11223',
                'status': 'Available',
                'capacity_info': '30 Units (Men/Women/Disabled)',
            },
            {
                'name': 'Shelter Camp 12 — Night Stay Grounds',
                'category': 'Shelter',
                'details': 'Weatherproof waterproof tents, clean bedding, charging points, and security guard.',
                'latitude': 18.5204,
                'longitude': 73.8567,
                'address': 'Pune Municipal Corporation Grounds, Shivajinagar',
                'contact_number': '+91 98212 99887',
                'status': 'Available',
                'capacity_info': '120 Sleeping Cots Available',
            },
            {
                'name': 'Traffic Checkpoint 4 & Police Control',
                'category': 'Police',
                'details': 'Police assistance booth, traffic diversion control, and missing person registration.',
                'latitude': 18.7301,
                'longitude': 73.7621,
                'address': 'Chakan Highway Junction',
                'contact_number': '112 / +91 98230 00100',
                'status': 'Active',
                'capacity_info': '24x7 Patrol Unit Stationed',
            },
            {
                'name': 'Wari Central Information & Help Desk',
                'category': 'Help Desk',
                'details': 'Lost & Found registration, route map guidance, PA announcements in Marathi & English.',
                'latitude': 18.6769,
                'longitude': 73.8967,
                'address': 'Alandi Temple Complex Gate 1',
                'contact_number': '+91 98222 33445',
                'status': 'Active',
                'capacity_info': 'Bilingual Support Staff',
            },
            {
                'name': 'Jejuri Pilgrimage Rest & Water Facility',
                'category': 'Water',
                'details': 'Filtered drinking water taps and ORS hydration packets.',
                'latitude': 18.2778,
                'longitude': 74.1583,
                'address': 'Jejuri Temple Base, Jejuri',
                'contact_number': '+91 97654 32100',
                'status': 'Available',
                'capacity_info': '30,000L Reserve Tank',
            },
            {
                'name': 'Pandharpur Shri Vitthal Temple Help Desk',
                'category': 'Help Desk',
                'details': 'Darshan queue assistance, senior citizen support, wheelchair service, and emergency help.',
                'latitude': 17.6775,
                'longitude': 75.3283,
                'address': 'Main Vitthal Temple Entry Gate, Pandharpur',
                'contact_number': '+91 98230 55443',
                'status': 'Active',
                'capacity_info': '24x7 Multi-lingual Staff',
            },
        ]

        created_count = 0
        for data in initial_points:
            point, created = ServicePoint.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {created_count} service points into the database.')
        )
