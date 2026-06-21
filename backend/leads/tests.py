from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from accounts.models import Company, CustomUser

from admissions.models import Student

from .journey_board import resolve_lead_stage, resolve_student_stage
from .journey_constants import JOURNEY_STAGES, STAGE_LABELS
from .models import Lead


class JourneyConstantsTests(SimpleTestCase):
    def test_twelve_stages(self):
        self.assertEqual(len(JOURNEY_STAGES), 12)
        self.assertEqual(len(STAGE_LABELS), 12)


class ResolveLeadStageTests(SimpleTestCase):
    def test_new_lead_statuses(self):
        lead = SimpleNamespace(status='follow_up')
        self.assertEqual(resolve_lead_stage(lead), 'new_lead')

    def test_pipeline_status(self):
        lead = SimpleNamespace(status='qualified')
        self.assertEqual(resolve_lead_stage(lead), 'qualified')

    def test_converted_returns_none(self):
        lead = SimpleNamespace(status='converted')
        self.assertIsNone(resolve_lead_stage(lead))


class ResolveStudentStageTests(SimpleTestCase):
    def test_journey_stage_override(self):
        student = SimpleNamespace(
            journey_stage='departure',
            status='counselling',
        )
        self.assertEqual(resolve_student_stage(student, [], []), 'departure')

    def test_visa_approved_from_case(self):
        student = SimpleNamespace(
            journey_stage='',
            status='counselling',
        )
        visa = SimpleNamespace(status='approved')
        self.assertEqual(
            resolve_student_stage(student, [], [visa]),
            'visa_approved',
        )


class JourneyBoardMoveTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.user = CustomUser.objects.create_user(
            username='admin',
            password='pass1234',
            company=self.company,
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Jane',
            last_name='Doe',
            phone='9999999999',
            status='new',
        )

    def test_move_lead_to_qualified(self):
        from .journey_board import move_to_stage

        card = move_to_stage(
            'lead',
            self.lead.id,
            'qualified',
            self.company,
            self.user,
        )
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, 'qualified')
        self.assertEqual(card['stage'], 'qualified')

    def test_move_student_departure(self):
        from .journey_board import move_to_stage

        student = Student.objects.create(
            company=self.company,
            lead=self.lead,
            student_id='STU-001',
            status='counselling',
        )
        self.lead.status = 'converted'
        self.lead.save()

        card = move_to_stage(
            'student',
            student.id,
            'departure',
            self.company,
            self.user,
        )
        student.refresh_from_db()
        self.assertEqual(student.journey_stage, 'departure')
        self.assertEqual(card['stage'], 'departure')


class LeadConversionTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Convert Co')
        self.user = CustomUser.objects.create_user(
            username='convertadmin',
            password='pass1234',
            company=self.company,
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Alex',
            last_name='Lee',
            phone='8888888888',
            status='interested',
        )

    def test_convert_from_interested(self):
        from .conversion_service import convert_lead_to_student

        student = convert_lead_to_student(
            self.lead,
            self.user,
        )

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, 'converted')
        self.assertEqual(student.lead_id, self.lead.id)
        self.assertTrue(
            Student.objects.filter(lead=self.lead).exists(),
        )

    def test_reject_new_lead(self):
        from rest_framework.exceptions import ValidationError

        from .conversion_service import convert_lead_to_student

        self.lead.status = 'new'
        self.lead.save()

        with self.assertRaises(ValidationError):
            convert_lead_to_student(self.lead, self.user)

    def test_reject_not_interested(self):
        from rest_framework.exceptions import ValidationError

        from .conversion_service import convert_lead_to_student

        self.lead.status = 'not_interested'
        self.lead.save()

        with self.assertRaises(ValidationError):
            convert_lead_to_student(self.lead, self.user)
