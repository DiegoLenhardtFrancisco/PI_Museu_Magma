from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from usuarios.models import CustomUser

from .models import FixedCostEntry


def make_entry(user, category='RENT', value='500.00', days_offset=10, entry_status='PENDING', description=''):
    """
    Helper to create a FixedCostEntry quickly in tests.
    days_offset: how many days from today the due_date will be (negative = past).
    """
    return FixedCostEntry.objects.create(
        category=category,
        description=description,
        value=value,
        due_date=date.today() + timedelta(days=days_offset),
        status=entry_status,
        created_by=user,
        updated_by=user,
    )


class FixedCostCRUDTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123',
            user_type='ADMIN',
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('fixed-cost-entry-list')

    # --- Authentication ---

    def test_unauthenticated_user_cannot_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Create ---

    def test_create_entry_with_valid_data(self):
        data = {
            'category': 'ELECTRICITY',
            'description': 'Conta de Luz Abril',
            'value': '350.00',
            'due_date': '2026-04-10',
            'status': 'PENDING',
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FixedCostEntry.objects.count(), 1)
        self.assertEqual(response.data['category'], 'ELECTRICITY')
        self.assertEqual(response.data['category_display'], 'Luz')

    def test_create_entry_without_description(self):
        """Description is optional — should succeed without it."""
        data = {
            'category': 'WATER',
            'value': '120.00',
            'due_date': '2026-04-15',
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_entry_with_negative_value_fails(self):
        data = {
            'category': 'RENT',
            'value': '-100.00',
            'due_date': '2026-04-05',
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_entry_default_status_is_pending(self):
        data = {
            'category': 'INTERNET',
            'value': '200.00',
            'due_date': '2026-04-20',
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')

    # --- Read ---

    def test_list_entries(self):
        make_entry(self.user, category='RENT')
        make_entry(self.user, category='WATER')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_retrieve_single_entry(self):
        entry = make_entry(self.user, description='Aluguel Abril')
        url = reverse('fixed-cost-entry-detail', kwargs={'pk': entry.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Aluguel Abril')

    # --- Update ---

    def test_partial_update_value(self):
        entry = make_entry(self.user, value='500.00')
        url = reverse('fixed-cost-entry-detail', kwargs={'pk': entry.pk})
        response = self.client.patch(url, {'value': '550.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        self.assertEqual(str(entry.value), '550.00')

    def test_marking_as_paid_sets_paid_at(self):
        """When status changes to PAID, paid_at must be set to today."""
        entry = make_entry(self.user, entry_status='PENDING')
        url = reverse('fixed-cost-entry-detail', kwargs={'pk': entry.pk})
        response = self.client.patch(url, {'status': 'PAID'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        self.assertIsNotNone(entry.paid_at)
        self.assertEqual(entry.paid_at, date.today())

    def test_marking_as_pending_clears_paid_at(self):
        """When status goes back to PENDING, paid_at must be cleared."""
        entry = make_entry(self.user, entry_status='PAID')
        entry.paid_at = date.today()
        entry.save()
        url = reverse('fixed-cost-entry-detail', kwargs={'pk': entry.pk})
        response = self.client.patch(url, {'status': 'PENDING'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        self.assertIsNone(entry.paid_at)

    # --- Delete ---

    def test_delete_entry(self):
        entry = make_entry(self.user)
        url = reverse('fixed-cost-entry-detail', kwargs={'pk': entry.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FixedCostEntry.objects.count(), 0)


class FixedCostFilterTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123',
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('fixed-cost-entry-list')

        # Entry in April 2026
        FixedCostEntry.objects.create(
            category='RENT',
            value='2000.00',
            due_date='2026-04-05',
            status='PENDING',
            created_by=self.user,
            updated_by=self.user,
        )
        # Entry in March 2026
        FixedCostEntry.objects.create(
            category='RENT',
            value='2000.00',
            due_date='2026-03-05',
            status='PAID',
            paid_at='2026-03-04',
            created_by=self.user,
            updated_by=self.user,
        )
        # Different category in April 2026
        FixedCostEntry.objects.create(
            category='ELECTRICITY',
            value='350.00',
            due_date='2026-04-10',
            status='PENDING',
            created_by=self.user,
            updated_by=self.user,
        )

    def test_filter_by_month_returns_only_that_month(self):
        response = self.client.get(self.list_url, {'month': '2026-04'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_month_march(self):
        response = self.client.get(self.list_url, {'month': '2026-03'})
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_category(self):
        response = self.client.get(self.list_url, {'category': 'ELECTRICITY'})
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_status_pending(self):
        response = self.client.get(self.list_url, {'status': 'PENDING'})
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_status_paid(self):
        response = self.client.get(self.list_url, {'status': 'PAID'})
        self.assertEqual(response.data['count'], 1)

    def test_invalid_month_format_returns_all(self):
        """Invalid month param is silently ignored — returns all entries."""
        response = self.client.get(self.list_url, {'month': 'abril-2026'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)


class FixedCostIsOverdueTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123',
        )
        self.client.force_authenticate(user=self.user)

    def test_overdue_pending_entry_has_is_overdue_true(self):
        """A pending entry with a past due_date must have is_overdue=True."""
        entry = make_entry(self.user, days_offset=-5, entry_status='PENDING')
        url = reverse('fixed-cost-entry-detail', kwargs={'pk': entry.pk})
        response = self.client.get(url)
        self.assertTrue(response.data['is_overdue'])

    def test_future_pending_entry_is_not_overdue(self):
        entry = make_entry(self.user, days_offset=10, entry_status='PENDING')
        url = reverse('fixed-cost-entry-detail', kwargs={'pk': entry.pk})
        response = self.client.get(url)
        self.assertFalse(response.data['is_overdue'])

    def test_paid_entry_is_never_overdue(self):
        """Even if the due_date is in the past, a PAID entry is not overdue."""
        entry = make_entry(self.user, days_offset=-5, entry_status='PAID')
        url = reverse('fixed-cost-entry-detail', kwargs={'pk': entry.pk})
        response = self.client.get(url)
        self.assertFalse(response.data['is_overdue'])


class FixedCostSummaryTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123',
        )
        self.client.force_authenticate(user=self.user)
        self.summary_url = reverse('fixed-cost-entry-summary')

        FixedCostEntry.objects.create(
            category='RENT', value='2000.00', due_date='2026-04-05',
            status='PENDING', created_by=self.user, updated_by=self.user,
        )
        FixedCostEntry.objects.create(
            category='ELECTRICITY', value='350.00', due_date='2026-04-10',
            status='PENDING', created_by=self.user, updated_by=self.user,
        )
        FixedCostEntry.objects.create(
            category='WATER', value='120.00', due_date='2026-04-15',
            status='PAID', created_by=self.user, updated_by=self.user,
        )

    def test_summary_returns_correct_totals(self):
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_pending'], '2350.00')
        self.assertEqual(response.data['total_paid'], '120.00')
        self.assertEqual(response.data['total_overall'], '2470.00')

    def test_summary_filtered_by_month(self):
        # Add entry in a different month — should not affect April summary
        FixedCostEntry.objects.create(
            category='INTERNET', value='200.00', due_date='2026-03-20',
            status='PENDING', created_by=self.user, updated_by=self.user,
        )
        response = self.client.get(self.summary_url, {'month': '2026-04'})
        self.assertEqual(response.data['total_overall'], '2470.00')

    def test_summary_empty_database_returns_zeros(self):
        FixedCostEntry.objects.all().delete()
        response = self.client.get(self.summary_url)
        self.assertEqual(response.data['total_pending'], '0.00')
        self.assertEqual(response.data['total_paid'], '0.00')
        self.assertEqual(response.data['total_overall'], '0.00')

    def test_unauthenticated_cannot_access_summary(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)