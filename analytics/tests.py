from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from produtos.models import Product
from usuarios.models import CustomUser
from vendas.models import Customer, Sale, SaleItem


class DashboardStructureTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="pass123",
            user_type="ADMIN",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("analytics-dashboard")

    def test_returns_200_for_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_401_for_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response_has_all_top_level_keys(self):
        response = self.client.get(self.url)
        expected_keys = {"period", "revenue", "sales", "products", "visitors"}
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_revenue_section_has_expected_keys(self):
        response = self.client.get(self.url)
        expected_keys = {"total", "by_month", "by_payment_method"}
        self.assertEqual(set(response.data["revenue"].keys()), expected_keys)

    def test_sales_section_has_expected_keys(self):
        response = self.client.get(self.url)
        expected_keys = {"total_count", "average_ticket", "total_discount"}
        self.assertEqual(set(response.data["sales"].keys()), expected_keys)

    def test_products_section_has_expected_keys(self):
        response = self.client.get(self.url)
        expected_keys = {"top_selling", "low_stock", "low_stock_count"}
        self.assertEqual(set(response.data["products"].keys()), expected_keys)

    def test_visitors_section_has_expected_keys(self):
        response = self.client.get(self.url)
        expected_keys = {
            "total_count",
            "by_type",
            "by_month",
            "average_duration_minutes",
        }
        self.assertEqual(set(response.data["visitors"].keys()), expected_keys)


class DashboardDateFilterTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="pass123",
            user_type="ADMIN",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("analytics-dashboard")

    def test_valid_date_filter_returns_200(self):
        response = self.client.get(
            self.url,
            {"start_date": "2025-01-01", "end_date": "2025-12-31"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_period_is_echoed_back_in_response(self):
        response = self.client.get(
            self.url,
            {"start_date": "2025-01-01", "end_date": "2025-06-30"},
        )
        self.assertEqual(response.data["period"]["start_date"], "2025-01-01")
        self.assertEqual(response.data["period"]["end_date"], "2025-06-30")

    def test_invalid_start_date_format_returns_400(self):
        response = self.client.get(self.url, {"start_date": "01/01/2025"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_invalid_end_date_format_returns_400(self):
        response = self.client.get(self.url, {"end_date": "yesterday"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_date_after_end_date_returns_400(self):
        response = self.client.get(
            self.url,
            {"start_date": "2025-12-31", "end_date": "2025-01-01"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DashboardDataCorrectnessTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="pass123",
            user_type="ADMIN",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("analytics-dashboard")

        self.product1 = Product.objects.create(
            name="Ametista",
            code="A001",
            cost_price="50.00",
            profit_margin="100.00",
            quantity="100",
            unit_of_measure="UNIT",
            category="MINERAL",
            created_by=self.user,
        )

        self.product2 = Product.objects.create(
            name="Fóssil",
            code="F001",
            cost_price="80.00",
            profit_margin="50.00",
            quantity="0",
            minimum_quantity="5",
            unit_of_measure="UNIT",
            category="FOSSIL",
            created_by=self.user,
        )

        self.customer = Customer.objects.create(
            name="Cliente Teste",
            document="12345678900",
            customer_type="PF",
            phone="11999999999",
        )

        self.sale = Sale.objects.create(
            customer=self.customer,
            payment_method="PIX",
            status="COMPLETED",
            total_amount="300.00",
            total_cost="130.00",
            discount="0",
            created_by=self.user,
            updated_by=self.user,
        )

        SaleItem.objects.create(
            sale=self.sale,
            product=self.product1,
            quantity="2",
            unit_price="100.00",
        )

        SaleItem.objects.create(
            sale=self.sale,
            product=self.product2,
            quantity="1",
            unit_price="100.00",
        )

    def test_sales_count_is_correct(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["sales"]["total_count"], 1)

    def test_revenue_total_is_correct(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["revenue"]["total"], "300.00")

    def test_low_stock_count_is_correct(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["products"]["low_stock_count"], 1)
        self.assertEqual(
            response.data["products"]["low_stock"][0]["product_name"],
            "Fóssil",
        )

    def test_top_selling_includes_both_products(self):
        response = self.client.get(self.url)
        top = response.data["products"]["top_selling"]
        product_names = [item["product_name"] for item in top]

        self.assertIn("Ametista", product_names)
        self.assertIn("Fóssil", product_names)

    def test_by_payment_method_shows_pix(self):
        response = self.client.get(self.url)
        methods = [
            item["method"] for item in response.data["revenue"]["by_payment_method"]
        ]
        self.assertIn("PIX", methods)

    def test_date_filter_excludes_data_outside_range(self):
        response = self.client.get(
            self.url,
            {"start_date": "2000-01-01", "end_date": "2000-12-31"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sales"]["total_count"], 0)
        self.assertEqual(response.data["revenue"]["total"], "0.00")
