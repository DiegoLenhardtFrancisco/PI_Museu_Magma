from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from usuarios.models import CustomUser
from produtos.models import Product
from .models import Sale, SaleItem

class SaleAPITests(APITestCase):
    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = CustomUser.objects.create_user(
            username='testseller', email='seller@example.com', password='password123'
        )
        self.client.force_authenticate(user=self.user)

        self.product1 = Product.objects.create(
            name="Ametista", code="P001", cost_price="100.00",
            profit_margin="50.00", quantity="10", unit_of_measure="UNIT",
            category="MINERAL", user=self.user
        )
        self.product2 = Product.objects.create(
            name="Fóssil", code="P002", cost_price="200.00",
            profit_margin="50.00", quantity="5", unit_of_measure="UNIT",
            category="FOSSIL", user=self.user
        )

    def test_create_sale_success(self):
        """
        Ensure we can create a new sale with valid data.
        """
        url = reverse('sale-list')
        data = {
            "payment_method": "PIX",
            "notes": "Test sale via API",
            "items_to_create": [
                {"product_id": self.product1.id, "quantity": "2.00"},
                {"product_id": self.product2.id, "quantity": "1.00"}
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(SaleItem.objects.count(), 2)

        sale = Sale.objects.first()
        expected_total = (self.product1.sale_price * 2) + (self.product2.sale_price * 1)
        self.assertEqual(sale.total_amount, expected_total)

        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.quantity, Decimal('8.00'))
        self.assertEqual(self.product2.quantity, Decimal('4.00'))

    def test_create_sale_insufficient_stock(self):
        """
        Ensure API rejects a sale if product stock is insufficient.
        """
        url = reverse('sale-list')
        data = {
            "payment_method": "CASH",
            "items_to_create": [
                {"product_id": self.product1.id, "quantity": "11.00"}
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Estoque insuficiente", str(response.data))

        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(SaleItem.objects.count(), 0)

        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, Decimal('10.00'))

    def test_list_sales(self):
        """
        Ensure we can list sales.
        """
        self.test_create_sale_success()

        url = reverse('sale-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(len(response.data['results'][0]['items']), 2)
    
    def test_create_sale_with_no_items(self):
        """
        Ensures that the API rejects a sale submitted without any items.
        """
        url = reverse('sale-list')
        data = {"payment_method": "DEBIT", "items_to_create": []}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items_to_create", response.data['errors']['detail'])

    def test_create_sale_with_invalid_product_id(self):
        """
        Ensures that the API rejects a sale referencing a non-existent product.
        """
        url = reverse('sale-list')
        invalid_product_id = 999
        data = {
            "payment_method": "CREDIT",
            "items_to_create": [{"product_id": invalid_product_id, "quantity": "1.00"}]
        }

        with self.assertRaises(Product.DoesNotExist):
            self.client.post(url, data, format='json')

    def test_list_sales(self):
        """
        Ensures that we can list existing sales.
        """
        self.test_create_sale_success()
        url = reverse('sale-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(len(response.data['results'][0]['items']), 2)

    def test_retrieve_sale_detail(self):
        """
        Ensures that we can see the details of a specific sale.
        """
        self.test_create_sale_success()
        sale = Sale.objects.first()
        url = reverse('sale-detail', kwargs={'pk': sale.pk})
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], sale.id)
        self.assertEqual(len(response.data['items']), 2)

    def test_unauthenticated_user_cannot_list_sales(self):
        """
        Ensures that an unauthenticated user cannot access the sales list.
        """
        self.client.force_authenticate(user=None) 
        url = reverse('sale-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)