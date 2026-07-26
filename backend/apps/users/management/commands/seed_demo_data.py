"""
WariMitra — Seed Demo Data Command
===================================
Usage:
    python manage.py seed_demo_data

Creates all demo users, pilgrim profiles, dindi groups, medical camps,
SOS incidents, NGO resources, and temple queues needed for a full demo.
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
    {
        "emergency_type": "Lost_Person",
        "priority": "High",
        "lat": "18.7100",
        "lng": "73.8200",
        "desc": "8-year old child separated from family near water distribution point. Child wearing saffron kurta.",
        "status": "New",
    },
    {
        "emergency_type": "Medical",
        "priority": "Medium",
        "lat": "18.6950",
        "lng": "73.8750",
        "desc": "Pilgrim reporting severe dehydration symptoms. Conscious but disoriented.",
        "status": "Resolved",
    },
    {
        "emergency_type": "Women_Safety",
        "priority": "High",
        "lat": "18.7050",
        "lng": "73.8600",
        "desc": "Group of women pilgrims reporting harassment near rest camp 12.",
        "status": "New",
    },
]

NGO_RESOURCES = [
    {"name": "Drinking Water Packets 500ml", "type": "Water", "unit": "Packets", "qty": 50000, "lat": "18.6824", "lng": "73.8973"},
    {"name": "Dal-Baati Meals", "type": "Food", "unit": "Thali", "qty": 10000, "lat": "18.7100", "lng": "73.8100"},
    {"name": "ORS Sachets", "type": "Medicine", "unit": "Sachets", "qty": 20000, "lat": "18.6900", "lng": "73.8700"},
    {"name": "Woolen Blankets", "type": "Blanket", "unit": "Pieces", "qty": 5000, "lat": "18.7200", "lng": "73.8300"},
]

TEMPLE_QUEUES = [
    {"type": "General", "gate": "Gate-1-Main", "capacity": 5000, "current": 3200, "wait_min": 260},
    {"type": "Senior Citizen", "gate": "Gate-2-Senior", "capacity": 1000, "current": 450, "wait_min": 80},
    {"type": "VIP", "gate": "Gate-3-VIP", "capacity": 200, "current": 60, "wait_min": 20},
    {"type": "Women", "gate": "Gate-4-Women", "capacity": 2000, "current": 1800, "wait_min": 180},
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
                self.stdout.write(f"   [OK] Created: {cred['username']} [{cred['role']}]")
            else:
                self.stdout.write(f"   [SKIP] Exists: {cred['username']}")
            users[cred["role"]] = user

        pilgrim_users = list(User.objects.filter(role="PILGRIM")[:3])

        # -- 2. Create Pilgrim Profiles --
        self.stdout.write("\n[+] Creating pilgrim profiles...")
        from apps.pilgrims.models import PilgrimProfile, Dindi, FamilyGroup, EmergencyContact
        for i, pilgrim_user in enumerate(pilgrim_users):
            profile, created = PilgrimProfile.objects.get_or_create(
                user=pilgrim_user,
                defaults={
                    "age": random.choice([45, 62, 38, 55, 70]),
                    "gender": random.choice(["Male", "Female"]),
                    "blood_group": random.choice(["A+", "B+", "O+", "AB+"]),
                    "medical_conditions": random.choice(["None", "Hypertension", "Diabetes", "None"]),
                    "qr_id": f"WM-PILGRIM-{1000 + i}",
                }
            )
            if created:
                self.stdout.write(f"   [OK] Profile for {pilgrim_user.username}")
            # Emergency Contact
            EmergencyContact.objects.get_or_create(
                pilgrim=pilgrim_user,
                mobile=f"9800000{i:03d}",
                defaults={
                    "name": f"Emergency Contact {i+1}",
                    "relationship": random.choice(["Spouse", "Son", "Daughter"]),
                }
            )

        # -- 3. Create Dindi Groups --
        self.stdout.write("\n[+] Creating Dindi groups...")
        leader = users.get("DINDI_LEADER")
        for d in DINDI_GROUPS:
            dindi, created = Dindi.objects.get_or_create(
                registration_number=d["reg_no"],
                defaults={"name": d["name"], "leader": leader}
            )
            if created:
                self.stdout.write(f"   [OK] Dindi: {d['name']}")

        # -- 4. Create Medical Camps --
        self.stdout.write("\n[+] Creating medical camps...")
        from apps.medical.models import MedicalCamp, Hospital, Ambulance
        for camp in MEDICAL_CAMPS:
            c, created = MedicalCamp.objects.get_or_create(
                name=camp["name"],
                defaults={
                    "latitude": camp["lat"],
                    "longitude": camp["lng"],
                    "doctors_available": camp["doctors"],
                    "status": "Active",
                }
            )
            if created:
                self.stdout.write(f"   [OK] Camp: {camp['name']}")

        # Create ambulances
        for i in range(1, 6):
            Ambulance.objects.get_or_create(
                vehicle_number=f"MH12-WM-{1000+i}",
                defaults={
                    "driver": users.get("MEDICAL_STAFF"),
                    "latitude": "18.6824",
                    "longitude": "73.8973",
                    "status": random.choice(["Available", "Dispatched", "Available"]),
                }
            )

        # -- 5. Create SOS Incidents --
        self.stdout.write("\n[+] Creating SOS incidents...")
        from apps.sos.models import EmergencyIncident
        for i, inc in enumerate(SOS_INCIDENTS):
            reporter = pilgrim_users[i % len(pilgrim_users)]
            incident, created = EmergencyIncident.objects.get_or_create(
                description=inc["desc"],
                defaults={
                    "user": reporter,
                    "emergency_type": inc["emergency_type"],
                    "priority": inc["priority"],
                    "latitude": inc["lat"],
                    "longitude": inc["lng"],
                    "status": inc["status"],
                }
            )
            if created:
                self.stdout.write(f"   [OK] Incident: [{inc['priority']}] {inc['emergency_type']}")

        # -- 6. Create NGO Resources --
        self.stdout.write("\n[+] Creating NGO resources & inventory...")
        from apps.ngo.models import Resource, Inventory
        ngo = users.get("NGO_COORDINATOR")
        for res in NGO_RESOURCES:
            resource, created = Resource.objects.get_or_create(
                name=res["name"],
                defaults={
                    "ngo_coordinator": ngo,
                    "resource_type": res["type"],
                    "unit": res["unit"],
                }
            )
            Inventory.objects.get_or_create(
                resource=resource,
                defaults={
                    "quantity": res["qty"],
                    "latitude": res["lat"],
                    "longitude": res["lng"],
                    "status": "Available",
                }
            )
            if created:
                self.stdout.write(f"   [OK] Resource: {res['name']} ({res['qty']} {res['unit']})")

        # -- 7. Create Temple Queues --
        self.stdout.write("\n[+] Creating temple queue data...")
        from apps.temple.models import TempleQueue
        for q in TEMPLE_QUEUES:
            queue, created = TempleQueue.objects.get_or_create(
                gate_id=q["gate"],
                defaults={
                    "queue_type": q["type"],
                    "capacity": q["capacity"],
                    "current_count": q["current"],
                    "average_wait_time": q["wait_min"],
                    "status": "Open" if q["current"] < q["capacity"] else "Full",
                }
            )
            if created:
                self.stdout.write(f"   [OK] Queue: {q['type']} at {q['gate']} - Wait: {q['wait_min']} mins")

        # -- Summary --
        self.stdout.write(self.style.SUCCESS("""
==========================================================
         [OK] Demo Seed Complete - WariMitra Ready!
==========================================================

DEMO LOGIN CREDENTIALS
----------------------------------------------------------
  Role               Username           Password
  Super Admin        superadmin         WariMitra@2025!
  Govt Admin         govt_admin         GovtAdmin@123
  Medical Officer    medical_officer    MedOfficer@123
  Police Officer     police_officer     Police@1234
  NGO Coordinator    ngo_coord          NGO@123456
  Volunteer          volunteer_1        Volunteer@123
  Dindi Leader       dindi_leader       Dindi@Leader1
  Pilgrim 1          pilgrim_1          Pilgrim@123
  Pilgrim 2          pilgrim_2          Pilgrim@234
  Pilgrim 3          pilgrim_3          Pilgrim@345
----------------------------------------------------------
  Django Admin URL:  http://localhost:8000/admin/
----------------------------------------------------------
"""))
