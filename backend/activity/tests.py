from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from accounts.models import Company, CustomUser

from admissions.models import Student

from activity.timeline_constants import (
    ACTIVITY_EVENT_TYPES,
    EVENT_LEAD_CREATED,
    EVENT_STUDENT_CONVERTED,
)
from activity.timeline_service import (
    get_lead_timeline,
    get_student_timeline,
    record_lead_event,
    record_student_event,
)
from leads.models import Lead


class TimelineConstantsTests(SimpleTestCase):
    def test_thirteen_event_types(self):
        self.assertEqual(len(ACTIVITY_EVENT_TYPES), 13)


class LeadTimelineServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Timeline Co')
        self.user = CustomUser.objects.create_user(
            username='tluser',
            password='pass1234',
            company=self.company,
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Alex',
            last_name='Lee',
            phone='8888888888',
            status='new',
        )

    def test_record_and_fetch_lead_event(self):
        record_lead_event(
            self.lead,
            EVENT_LEAD_CREATED,
            description='Manual entry.',
            user=self.user,
        )

        events = get_lead_timeline(self.lead)

        self.assertTrue(
            any(
                e['event_type'] == EVENT_LEAD_CREATED
                and e['description'] == 'Manual entry.'
                for e in events
            ),
        )

    def test_filter_lead_events(self):
        record_lead_event(
            self.lead,
            EVENT_LEAD_CREATED,
            user=self.user,
        )

        filtered = get_lead_timeline(
            self.lead,
            EVENT_LEAD_CREATED,
        )

        self.assertGreaterEqual(len(filtered), 1)


class StudentTimelineServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Student TL Co')
        self.user = CustomUser.objects.create_user(
            username='stuser',
            password='pass1234',
            company=self.company,
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Sam',
            last_name='Kim',
            phone='7777777777',
            status='converted',
        )
        self.student = Student.objects.create(
            company=self.company,
            lead=self.lead,
            student_id='STU-100',
        )

    def test_record_student_event(self):
        record_student_event(
            self.student,
            EVENT_STUDENT_CONVERTED,
            user=self.user,
        )

        events = get_student_timeline(self.student)

        self.assertEqual(len(events), 1)
        self.assertEqual(
            events[0]['action'],
            'Student Converted',
        )
