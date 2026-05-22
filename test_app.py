import unittest
import json
from unittest.mock import patch, MagicMock
from app import app

class RestaurantApiTestCase(unittest.TestCase):

    def setUp(self):
        """Executes before every single test. Sets up an in-memory test client."""
        self.app = app.test_client()
        self.app.testing = True

    # --- 1. UNIT TEST: HEALTH CHECK ROUTE ---
    @patch('routes.get_db_connection')
    def test_health_check_healthy(self, mock_get_db):
        """Verify health check returns 200 when DB connection works"""
        # Mock the database connection and cursor so we don't need a real running database container for this test
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        response = self.app.get('/health-check')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertTrue(data['database_connected'])

    # --- 2. INTEGRATION / LOGIC TEST: POST ORDER SUCCESS & MATH ---
    @patch('routes.get_db_connection')
    def test_place_order_success(self, mock_get_db):
        """Verify order calculation math works and returns 201 Created"""
        # Mock database row return: Item Name = 'Classic Burger', Price = 12.99
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('Classic Burger', 12.99)
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate a frontend POST payload ordering 2 burgers
        order_payload = {'item_id': 1, 'quantity': 2}
        
        response = self.app.post(
            '/order',
            data=json.dumps(order_payload),
            content_type='application/json'
        )
        data = json.loads(response.data)

        # Assertions: Did the API handle the business logic correctly?
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['receipt']['item_ordered'], 'Classic Burger')
        self.assertEqual(data['receipt']['quantity'], 2)
        # The key assertion: 12.99 * 2 should equal exactly 25.98
        self.assertEqual(data['receipt']['total_price'], 25.98)

    # --- 3. EDGE CASE TEST: POST ORDER MISSING DATA ---
    def test_place_order_missing_payload(self, *args):
        """Verify API safely rejects bad front-end payloads with a 400 Bad Request"""
        # Sending an empty dictionary missing 'item_id'
        bad_payload = {'quantity': 5}
        
        response = self.app.post(
            '/order',
            data=json.dumps(bad_payload),
            content_type='application/json'
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'fail')
        self.assertIn("Missing 'item_id'", data['message'])

    # --- 4. EDGE CASE TEST: ITEM NOT FOUND ---
    @patch('routes.get_db_connection')
    def test_place_order_item_not_found(self, mock_get_db):
        """Verify API responds with a 404 when ordering a dish that isn't on the menu"""
        # Mock database returning None (item doesn't exist)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        invalid_order = {'item_id': 999, 'quantity': 1}
        
        response = self.app.post(
            '/order',
            data=json.dumps(invalid_order),
            content_type='application/json'
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['status'], 'fail')
        self.assertIn("not found", data['message'])

if __name__ == '__main__':
    unittest.main()