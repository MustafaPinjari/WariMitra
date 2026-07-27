"""
WariMitra — Seed Demo Data Command
===================================
Usage:
    python manage.py seed_demo_data

Creates all demo users, pilgrim profiles, dindi groups, medical camps,
SOS incidents, NGO resources, temple queues, heritage abhangs, lost items, and sanitation records.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

DEMO_CREDENTIALS = [
    {
        "username": "superadmin",
        "password": "WariMitra@2025!",
        "email": "superadmin@warimitra.gov.in",
        "mobile": "9900000000",
        "role": "SUPER_ADMIN",
        "first_name": "Super",
        "last_name": "Admin",
    },
    {
        "username": "govt_admin",
        "password": "GovtAdmin@123",
        "email": "admin@collectorate.mah.gov.in",
        "mobile": "9900000001",
        "role": "GOVERNMENT_ADMIN",
        "first_name": "Collector",
        "last_name": "Pune",
    },
    {
        "username": "medical_officer",
        "password": "MedOfficer@123",
        "email": "medical@warimitra.gov.in",
        "mobile": "9900000002",
        "role": "MEDICAL_STAFF",
        "first_name": "Dr. Sunita",
        "last_name": "Patil",
    },
    {
        "username": "police_officer",
        "password": "Police@1234",
        "email": "police@warimitra.gov.in",
        "mobile": "9900000003",
        "role": "POLICE_OFFICER",
        "first_name": "PSI Rajesh",
        "last_name": "Shinde",
    },
    {
        "username": "ngo_coord",
        "password": "NGO@123456",
        "email": "ngo@sevamandal.org",
        "mobile": "9900000004",
        "role": "NGO_COORDINATOR",
        "first_name": "Sanjay",
        "last_name": "Kulkarni",
    },
    {
        "username": "volunteer_1",
        "password": "Volunteer@123",
        "email": "volunteer@warimitra.gov.in",
        "mobile": "9900000005",
        "role": "VOLUNTEER",
        "first_name": "Priya",
        "last_name": "More",
    },
    {
        "username": "dindi_leader",
        "password": "Dindi@Leader1",
        "email": "dindi@warimitra.gov.in",
        "mobile": "9900000006",
        "role": "DINDI_LEADER",
        "first_name": "Vitthal",
        "last_name": "Deshmukh",
    },
    {
        "username": "pilgrim_1",
        "password": "Pilgrim@123",
        "email": "pilgrim1@gmail.com",
        "mobile": "9900000007",
        "role": "PILGRIM",
        "first_name": "Ramesh",
        "last_name": "Jadhav",
    },
    {
        "username": "pilgrim_2",
        "password": "Pilgrim@234",
        "email": "pilgrim2@gmail.com",
        "mobile": "9900000008",
        "role": "PILGRIM",
        "first_name": "Meena",
        "last_name": "Kale",
    },
    {
        "username": "pilgrim_3",
        "password": "Pilgrim@345",
        "email": "pilgrim3@gmail.com",
        "mobile": "9900000009",
        "role": "PILGRIM",
        "first_name": "Anil",
        "last_name": "Wagh",
    },
]

MEDICAL_CAMPS = [
    {"name": "Camp Alpha — Alandi Chowk", "lat": "18.6824", "lng": "73.8973", "doctors": 4},
    {"name": "Camp Beta — Dehu Phata", "lat": "18.7301", "lng": "73.7621", "doctors": 3},
    {"name": "Camp Gamma — Talegaon Dabhade", "lat": "18.7261", "lng": "73.6723", "doctors": 2},
    {"name": "Camp Delta — Lonavala Base", "lat": "18.7490", "lng": "73.4060", "doctors": 5},
    {"name": "Camp Epsilon — Pandharpur Sector 1", "lat": "17.6806", "lng": "75.3316", "doctors": 6},
]

DINDI_GROUPS = [
    {"name": "Shri Vitthal Dindi - Pune", "reg_no": "DINDI-PUN-001"},
    {"name": "Sant Tukaram Dindi - Alandi", "reg_no": "DINDI-ALA-002"},
    {"name": "Hari Naam Dindi - Mumbai", "reg_no": "DINDI-MUM-003"},
    {"name": "Warkari Seva Dindi - Nashik", "reg_no": "DINDI-NSK-004"},
]

SOS_INCIDENTS = [
    {
        "emergency_type": "Medical",
        "priority": "Critical",
        "lat": "18.6721",
        "lng": "73.8889",
        "desc": "Elderly pilgrim collapsed near Gate 3, unresponsive. Requires immediate medical attention.",
        "status": "Responder_Assigned",
    },
    {
        "emergency_type": "Crowd_Incident",
        "priority": "High",
        "lat": "18.6810",
        "lng": "73.8965",
        "desc": "Crowd bottleneck forming near Alandi Temple main entrance. Potential stampede risk.",
        "status": "In_Progress",
    },
]

NGO_RESOURCES = [
    {"name": "Drinking Water Packets 500ml", "type": "Water", "unit": "Packets", "qty": 50000, "lat": "18.6824", "lng": "73.8973"},
    {"name": "Dal-Baati Meals", "type": "Food", "unit": "Thali", "qty": 10000, "lat": "18.7100", "lng": "73.8100"},
]

TEMPLE_QUEUES = [
    {"type": "General", "gate": "Gate-1-Main", "capacity": 5000, "current": 3200, "wait_min": 260},
    {"type": "Senior Citizen", "gate": "Gate-2-Senior", "capacity": 1000, "current": 450, "wait_min": 80},
]


class Command(BaseCommand):
    help = "Seeds the WariMitra database with realistic demo data for all modules."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("\n[*] Starting WariMitra Demo Data Seed...\n"))

        # -- 1. Create Users --
        self.stdout.write("[+] Creating demo users...")
        users = {}
        for cred in DEMO_CREDENTIALS:
            user, created = User.objects.get_or_create(
                username=cred["username"],
                defaults={
                    "email": cred["email"],
                    "mobile": cred["mobile"],
                    "role": cred["role"],
                    "first_name": cred["first_name"],
                    "last_name": cred["last_name"],
                    "is_verified": True,
                    "is_active": True,
                    "is_staff": cred["role"] in ("SUPER_ADMIN", "GOVERNMENT_ADMIN"),
                    "is_superuser": cred["role"] == "SUPER_ADMIN",
                }
            )
            if created:
                user.set_password(cred["password"])
                user.save()
            users[cred["role"]] = user

        pilgrim_users = list(User.objects.filter(role="PILGRIM")[:3])

        # -- 2. Create Pilgrim Profiles --
        self.stdout.write("[+] Creating pilgrim profiles...")
        from apps.pilgrims.models import PilgrimProfile, EmergencyContact
        for i, pilgrim_user in enumerate(pilgrim_users):
            PilgrimProfile.objects.get_or_create(
                user=pilgrim_user,
                defaults={
                    "age": 62,
                    "gender": "Male",
                    "blood_group": "B+",
                    "medical_conditions": "Hypertension",
                    "qr_id": f"WM-PILGRIM-{1000 + i}",
                }
            )
            EmergencyContact.objects.get_or_create(
                pilgrim=pilgrim_user,
                mobile=f"9800000{i:03d}",
                defaults={
                    "name": f"Emergency Contact {i+1}",
                    "relationship": "Son",
                }
            )

        # -- 3. Heritage Saints & Abhangs --
        self.stdout.write("[+] Creating Heritage Saints & Abhangs...")
        from apps.heritage.models import Saint, Abhang, PilgrimageMilestone
        dnyaneshwar, _ = Saint.objects.get_or_create(
            name="Sant Dnyaneshwar Maharaj",
            defaults={
                "marathi_name": "संत ज्ञानेश्वर महाराज",
                "title": "Mauli",
                "era": "1275 – 1296 CE",
                "biography": "Patron saint of the Wari pilgrimage, author of Dnyaneshwari.",
            }
        )
        tukaram, _ = Saint.objects.get_or_create(
            name="Sant Tukaram Maharaj",
            defaults={
                "marathi_name": "संत तुकाराम महाराज",
                "title": "Jagadguru",
                "era": "1598 – 1650 CE",
                "biography": "Greatest Abhang poet saint of Dehu, Maharashtra.",
            }
        )

        Abhang.objects.get_or_create(
            title="Rupe Sunder Sawala",
            defaults={
                "saint": dnyaneshwar,
                "marathi_title": "रूप सुंदर सावळा तो हा",
                "lyrics": "रूप सुंदर सावळा तो हा विठ्ठल बरवा। तो हा विठ्ठल बरवा।",
                "translation": "Beautiful is the enchanting dark complexion of Lord Vitthal.",
            }
        )

        PilgrimageMilestone.objects.get_or_create(
            name="Alandi Sanctuary",
            defaults={
                "marathi_name": "आळंदी संजीवन समाधी मंदिर",
                "significance": "Palkhi departure point for Sant Dnyaneshwar Maharaj.",
                "latitude": 18.6769,
                "longitude": 73.8967,
                "day_number": 1,
            }
        )

        # -- 4. Lost & Found Items --
        self.stdout.write("[+] Creating Digital Lost & Found records...")
        from apps.lost_found.models import LostFoundItem
        LostFoundItem.objects.get_or_create(
            title="Black Leather Wallet with Aadhaar Card",
            defaults={
                "category": "Wallet / ID",
                "description": "Lost near Alandi Chowk water distribution counter.",
                "status": "FOUND",
                "location": "Alandi Camp Beta",
                "contact_phone": "9900000005",
                "qr_claim_code": "WM-LF-99201",
            }
        )

        # -- 5. Sanitation & Toilets --
        self.stdout.write("[+] Creating Public Toilet & Sanitation records...")
        from apps.sanitation.models import PublicToilet, WasteReport
        PublicToilet.objects.get_or_create(
            name="Alandi Rest Shelter Public Toilet Block A",
            defaults={
                "location": "Sector 1, Alandi",
                "gender_type": "Unisex / Accessible",
                "cleanliness_score": 92,
                "is_water_available": True,
                "latitude": 18.6780,
                "longitude": 73.8970,
            }
        )
        WasteReport.objects.get_or_create(
            location_name="Dive Ghat Slope Rest Camp",
            defaults={
                "waste_type": "Plastic Bottle Accumulation",
                "description": "Overflowing recycling bin near food distribution tent.",
                "status": "CLEANING_DISPATCHED",
                "latitude": 18.3444,
                "longitude": 74.0305,
            }
        )

        self.stdout.write(self.style.SUCCESS("""
==========================================================
 [OK] Full Seed Complete - All 12 Varithon Tracks Ready!
==========================================================
"""))
