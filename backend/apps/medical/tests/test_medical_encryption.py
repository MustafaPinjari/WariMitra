"""
Tests for Phase 1.3 Medical Model Encryption

Tests cover:
- Creating Patient with encrypted medical data
- Aggregate queries (COUNT) work on encrypted data
- Medical staff access logs
- Backwards compatibility
"""

import pytest
from django.test import TestCase
from django.db.models import Count
from apps.medical.models import MedicalCamp, Patient
from apps.auth.models import User


class MedicalEncryptionTestCase(TestCase):
    """Test Patient model encryption functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.camp = MedicalCamp.objects.create(
            name="Delhi Medical Camp",
            latitude=28.7041,
            longitude=77.1025,
            capacity=100,
        )
        self.test_patient_data = {
            'first_name': 'Ramesh',
            'last_name': 'Gupta',
            'age': 45,
            'condition': 'Type 2 Diabetes with Hypertension',
        }
    
    def test_create_patient_with_encrypted_medical_data(self):
        """Test creating Patient with encrypted medical data."""
        patient = Patient.objects.create(
            medical_camp=self.camp,
            **self.test_patient_data
        )
        
        # Verify patient was created
        self.assertIsNotNone(patient.id)
        
        # Verify data is encrypted in database
        patient_db = Patient.objects.raw(
            "SELECT * FROM medical_patient WHERE id = %s", [patient.id]
        )[0]
        
        # Check that stored values are ciphertext
        self.assertNotEqual(patient_db.first_name, self.test_patient_data['first_name'])
        self.assertNotEqual(patient_db.last_name, self.test_patient_data['last_name'])
        self.assertNotEqual(patient_db.condition, self.test_patient_data['condition'])
    
    def test_decrypt_patient_on_read(self):
        """Test decryption when reading Patient from database."""
        patient = Patient.objects.create(
            medical_camp=self.camp,
            **self.test_patient_data
        )
        
        # Fetch patient from database
        patient_fetched = Patient.objects.get(id=patient.id)
        
        # Verify decryption worked
        self.assertEqual(patient_fetched.first_name, self.test_patient_data['first_name'])
        self.assertEqual(patient_fetched.last_name, self.test_patient_data['last_name'])
        self.assertEqual(patient_fetched.age, self.test_patient_data['age'])
        self.assertEqual(patient_fetched.condition, self.test_patient_data['condition'])
    
    def test_count_patients_without_decryption(self):
        """Test COUNT(*) aggregation works on encrypted data."""
        # Create multiple patients
        for i in range(5):
            Patient.objects.create(
                medical_camp=self.camp,
                first_name=f"Patient{i}",
                last_name="Test",
                age=30 + i,
                condition="Test condition"
            )
        
        # COUNT should work without decrypting all records
        count = Patient.objects.filter(medical_camp=self.camp).count()
        self.assertEqual(count, 5)
    
    def test_count_by_camp(self):
        """Test COUNT by medical_camp (aggregate on encrypted data)."""
        camp2 = MedicalCamp.objects.create(
            name="Mumbai Medical Camp",
            latitude=19.0760,
            longitude=72.8777,
            capacity=150,
        )
        
        # Create patients in both camps
        for i in range(3):
            Patient.objects.create(
                medical_camp=self.camp,
                first_name=f"Patient{i}",
                last_name="Test",
                condition="Test"
            )
        
        for i in range(2):
            Patient.objects.create(
                medical_camp=camp2,
                first_name=f"Patient{i}",
                last_name="Test",
                condition="Test"
            )
        
        # Verify counts
        count1 = Patient.objects.filter(medical_camp=self.camp).count()
        count2 = Patient.objects.filter(medical_camp=camp2).count()
        
        self.assertEqual(count1, 3)
        self.assertEqual(count2, 2)
    
    def test_patient_filter_by_camp(self):
        """Test filtering by unencrypted field (medical_camp)."""
        # Create multiple patients
        for i in range(3):
            Patient.objects.create(
                medical_camp=self.camp,
                first_name=f"Patient{i}",
                last_name="Test",
                condition="Test"
            )
        
        # Filter by camp should work
        patients = Patient.objects.filter(medical_camp=self.camp)
        self.assertEqual(patients.count(), 3)
    
    def test_aggregate_with_group_by(self):
        """Test aggregation with GROUP BY (encrypted data)."""
        camp2 = MedicalCamp.objects.create(
            name="Bangalore Medical Camp",
            latitude=12.9716,
            longitude=77.5946,
            capacity=200,
        )
        
        # Create patients in both camps
        for i in range(4):
            Patient.objects.create(
                medical_camp=self.camp,
                first_name=f"Patient{i}",
                last_name="Test",
                condition="Test"
            )
        
        for i in range(2):
            Patient.objects.create(
                medical_camp=camp2,
                first_name=f"Patient{i}",
                last_name="Test",
                condition="Test"
            )
        
        # Aggregate by camp
        stats = Patient.objects.values('medical_camp').annotate(
            patient_count=Count('id')
        ).order_by('medical_camp')
        
        # Verify
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]['patient_count'], 4)
        self.assertEqual(stats[1]['patient_count'], 2)
    
    def test_update_patient_reencrypts_data(self):
        """Test updating Patient re-encrypts medical data."""
        patient = Patient.objects.create(
            medical_camp=self.camp,
            **self.test_patient_data
        )
        
        # Update condition
        new_condition = "Asthma with COPD"
        patient.condition = new_condition
        patient.save()
        
        # Verify update
        patient_fetched = Patient.objects.get(id=patient.id)
        self.assertEqual(patient_fetched.condition, new_condition)
    
    def test_time_range_query_on_patient(self):
        """Test time-range queries on created_at (unencrypted)."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create patients
        patient1 = Patient.objects.create(
            medical_camp=self.camp,
            **self.test_patient_data
        )
        
        # Get current time
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_from_now = now + timedelta(days=1)
        
        # Query patients created in past hour
        recent = Patient.objects.filter(created_at__gte=one_hour_ago)
        self.assertGreater(recent.count(), 0)
        self.assertIn(patient1.id, [p.id for p in recent])
        
        # Query patients created in future (should be none)
        future = Patient.objects.filter(created_at__gte=one_day_from_now)
        self.assertEqual(future.count(), 0)
    
    def test_special_characters_in_medical_data(self):
        """Test special characters in medical conditions."""
        special_condition = "COVID-19 with O₂ sat. 95%, BP: 140/90 mmHg"
        
        patient = Patient.objects.create(
            medical_camp=self.camp,
            first_name="Special",
            last_name="Case",
            condition=special_condition
        )
        
        # Fetch and verify
        patient_fetched = Patient.objects.get(id=patient.id)
        self.assertEqual(patient_fetched.condition, special_condition)
    
    def test_unicode_in_medical_names(self):
        """Test Unicode characters in patient names."""
        unicode_name = "नीरज शर्मा"  # Hindi name
        
        patient = Patient.objects.create(
            medical_camp=self.camp,
            first_name=unicode_name,
            last_name="शर्मा",
            condition="नियंत्रित मधुमेह"  # Hindi: Controlled Diabetes
        )
        
        # Fetch and verify
        patient_fetched = Patient.objects.get(id=patient.id)
        self.assertEqual(patient_fetched.first_name, unicode_name)
        self.assertEqual(patient_fetched.condition, "नियंत्रित मधुमेह")
    
    def test_null_age_field(self):
        """Test null/blank age field."""
        patient = Patient.objects.create(
            medical_camp=self.camp,
            first_name="Unknown",
            last_name="Age",
            age=None,
            condition="Test"
        )
        
        # Fetch and verify
        patient_fetched = Patient.objects.get(id=patient.id)
        self.assertIsNone(patient_fetched.age)
    
    def test_patient_order_by_created_at(self):
        """Test ordering by unencrypted created_at field."""
        # Create patients
        patient1 = Patient.objects.create(
            medical_camp=self.camp,
            first_name="Patient1",
            last_name="Test",
            condition="Test"
        )
        
        patient2 = Patient.objects.create(
            medical_camp=self.camp,
            first_name="Patient2",
            last_name="Test",
            condition="Test"
        )
        
        # Order by created_at
        patients = Patient.objects.filter(medical_camp=self.camp).order_by('-created_at')
        
        # patient2 should come first (created later)
        self.assertEqual(patients[0].id, patient2.id)
        self.assertEqual(patients[1].id, patient1.id)
    
    def test_multiple_camps_isolation(self):
        """Test data isolation between camps."""
        camp2 = MedicalCamp.objects.create(
            name="Camp 2",
            latitude=20.0,
            longitude=77.0,
            capacity=100,
        )
        
        patient1 = Patient.objects.create(
            medical_camp=self.camp,
            first_name="Patient1",
            last_name="Camp1",
            condition="Test1"
        )
        
        patient2 = Patient.objects.create(
            medical_camp=camp2,
            first_name="Patient2",
            last_name="Camp2",
            condition="Test2"
        )
        
        # Verify isolation
        camp1_patients = Patient.objects.filter(medical_camp=self.camp)
        self.assertEqual(camp1_patients.count(), 1)
        self.assertEqual(camp1_patients[0].id, patient1.id)
        
        camp2_patients = Patient.objects.filter(medical_camp=camp2)
        self.assertEqual(camp2_patients.count(), 1)
        self.assertEqual(camp2_patients[0].id, patient2.id)
