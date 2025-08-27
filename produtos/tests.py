from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from usuarios.models import CustomUser
from .models import Product

class ProductAPITests(APITestCase):
    def setUp(self):
        """
        This method runs before each test.
        We'll create a user and authenticate them.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.product1 = Product.objects.create(
            name="Ametista",
            code="000001",
            cost_price="100.00",
            profit_margin="50.00",
            quantity="10",
            unit_of_measure="UNIT",
            category="MINERAL",
            user=self.user
        )
        self.product2 = Product.objects.create(
            name="Fóssil de Peixe",
            code="000002",
            cost_price="250.00",
            profit_margin="80.00",
            quantity="5",
            unit_of_measure="UNIT",
            category="FOSSIL",
            user=self.user
        )

    def test_list_products(self):
        """
        Ensure we can list all products.
        """
        url = reverse('product-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_product_detail(self):
        """
        Ensure we can retrieve a single product by its ID.
        """
        url = reverse('product-detail', kwargs={'pk': self.product1.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product1.name)

    def test_create_product(self):
        """
        Ensure we can create a new product.
        """
        url = reverse('product-list')
        data = {
            "name": "Quartzo Rosa",
            "cost_price": "50.00",
            "profit_margin": "100.00",
            "quantity": "20",
            "unit_of_measure": "UNIT",
            "category": "MINERAL"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)
        self.assertEqual(response.data['name'], 'Quartzo Rosa')

    def test_update_product(self):
        """
        Ensure we can update an existing product using PUT.
        """
        url = reverse('product-detail', kwargs={'pk': self.product1.pk})
        # For PUT, you usually need to send the full object
        data = {
            "name": "Ametista Polida",
            "cost_price": "120.00", # New price
            "profit_margin": "60.00",
            "quantity": "8", # Updated quantity
            "unit_of_measure": "UNIT",
            "category": "MINERAL"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Ametista Polida')
        
        # Refresh the object from the database to check the update
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, Decimal('8.00'))

    def test_partial_update_product(self):
        """
        Ensure we can partially update an existing product using PATCH.
        """
        url = reverse('product-detail', kwargs={'pk': self.product2.pk})
        # For PATCH, you only send the fields you want to change
        data = {
            "quantity": "3",
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.product2.refresh_from_db()
        self.assertEqual(self.product2.quantity, Decimal('3.00'))

    def test_delete_product(self):
        """
        Ensure we can delete a product.
        """
        url = reverse('product-detail', kwargs={'pk': self.product1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)

    def test_unauthenticated_user_cannot_access(self):
        """
        Ensure unauthenticated users receive a 401 Unauthorized error.
        """
        self.client.force_authenticate(user=None)
        url = reverse('product-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)