from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from usuarios.models import CustomUser

from .models import Product, StockMovement


class ProductAPITests(APITestCase):
    def setUp(self):
        """
        This method runs before each test.
        We'll create a user and authenticate them.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            user_type='STOCKCLERK',  # <-- ADICIONE ESTA LINHA
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
            created_by=self.user,
        )
        self.product2 = Product.objects.create(
            name="Fóssil de Peixe",
            code="000002",
            cost_price="250.00",
            profit_margin="80.00",
            quantity="5",
            unit_of_measure="UNIT",
            category="FOSSIL",
            created_by=self.user,
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
            "category": "MINERAL",
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
            "cost_price": "120.00",  # New price
            "profit_margin": "60.00",
            "quantity": "8",  # Updated quantity
            "unit_of_measure": "UNIT",
            "category": "MINERAL",
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

    def test_create_product_with_invalid_data(self):
        """
        Ensure API returns 400 Bad Request for invalid data.
        """
        url = reverse('product-list')
        data = {
            "name": "",  # Invalid: empty name
            "cost_price": "-50.00",  # Invalid: negative price
            "profit_margin": "100.00",
            "quantity": "20",
            "unit_of_measure": "UNIT",
            "category": "MINERAL",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.count(), 2)
        self.assertIn('name', response.data['errors']['detail'])
        self.assertIn('cost_price', response.data['errors']['detail'])

    def test_filter_product_by_category(self):
        """
        Ensure we can filter products by category.
        """
        url = f"{reverse('product-list')}?category=MINERAL"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Ametista')

    def test_search_product_by_name(self):
        """
        Ensure we can search products by name.
        """
        url = f"{reverse('product-list')}?search=Peixe"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Fóssil de Peixe')


class ProductAPIPermissionsTests(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            'admin', 'admin@test.com', 'pass123'
        )
        self.seller_user = CustomUser.objects.create_user(
            'seller', 'seller@test.com', 'pass123', user_type='SELLER'
        )
        self.stockclerk_user = CustomUser.objects.create_user(
            'stockclerk', 'stock@test.com', 'pass123', user_type='STOCKCLERK'
        )
        self.product = Product.objects.create(
            name="Turmalina",
            code="000003",
            cost_price="300.00",
            quantity="20",
            unit_of_measure="UNIT",
            category="MINERAL",
            created_by=self.admin_user,
        )

    def test_seller_can_list_products(self):
        """Seller MUST have read permission (GET)."""
        self.client.force_authenticate(user=self.seller_user)
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_seller_cannot_create_product(self):
        """Sellers MUST NOT have write permission (POST)."""
        self.client.force_authenticate(user=self.seller_user)
        data = {
            "name": "Produto Proibido",
            "cost_price": "10.00",
            "quantity": 1,
            "unit_of_measure": "UNIT",
            "category": "MINERAL",
        }
        response = self.client.post(reverse('product-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stockclerk_can_create_product(self):
        """The stock clerk MUST have write permission (POST)."""
        self.client.force_authenticate(user=self.stockclerk_user)
        data = {
            "name": "Quartzo Rosa",
            "cost_price": "50.00",
            "profit_margin": "100.00",
            "quantity": "20",
            "unit_of_measure": "UNIT",
            "category": "MINERAL",
        }
        response = self.client.post(reverse('product-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class StockMovementAPITests(APITestCase):
    def setUp(self):
        """
        Set up the test environment by creating a user and some products,
        which will automatically generate stock movements via signals.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)

        self.product = Product.objects.create(
            name="Turmalina",
            code="000003",
            cost_price="300.00",
            profit_margin="50.00",
            quantity="20",
            unit_of_measure="UNIT",
            category="MINERAL",
            created_by=self.user,
        )

    def test_list_stock_movements(self):
        """
        Ensure we can list all stock movements.
        """
        url = reverse('stock-movement-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['product_name'], self.product.name)

    def test_filter_stock_movements_by_type(self):
        """
        Ensure filtering by movement type works correctly.
        """
        self.product.quantity = 25
        self.product.save()

        url = f"{reverse('stock-movement-list')}?type=ENTRY"
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIn("Quantidade alterada", response.data['results'][0]['notes'])

    def test_cannot_create_stock_movement(self):
        """
        Ensure POST requests are not allowed.
        """
        url = reverse('stock-movement-list')
        data = {"product": self.product.pk, "type": "ENTRY", "quantity": "10"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_delete_stock_movement(self):
        """
        Ensure DELETE requests are not allowed.
        """
        movement = StockMovement.objects.first()
        url = reverse('stock-movement-detail', kwargs={'pk': movement.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
