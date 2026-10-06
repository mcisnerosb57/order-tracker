import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures ---

@pytest.fixture
def mock_storage():
    """Provides a mock storage object for tests."""
    mock = Mock()
    mock.get_order.return_value = None
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """Provides an OrderTracker instance initialized with the mock_storage."""
    return OrderTracker(mock_storage)

# --- Example tests provided by the course ---

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    mock_storage.save_order.assert_called_once()

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}
    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

# --- Constructor ---

class TestOrderTrackerInit:
    def test_raises_if_storage_missing_save_order(self):
        bad = Mock(spec=["get_order", "get_all_orders"])
        with pytest.raises(TypeError):
            OrderTracker(bad)

    def test_raises_if_storage_missing_get_order(self):
        bad = Mock(spec=["save_order", "get_all_orders"])
        with pytest.raises(TypeError):
            OrderTracker(bad)

    def test_raises_if_storage_missing_get_all_orders(self):
        bad = Mock(spec=["save_order", "get_order"])
        with pytest.raises(TypeError):
            OrderTracker(bad)


# --- add_order ---

class TestAddOrder:
    def test_default_status_is_pending(self, order_tracker, mock_storage):
        order_tracker.add_order("O1", "Laptop", 1, "C1")
        _, saved_data = mock_storage.save_order.call_args[0]
        assert saved_data["status"] == "pending"

    def test_stores_all_fields(self, order_tracker, mock_storage):
        order_tracker.add_order("O1", "Laptop", 2, "CUST99")
        _, saved_data = mock_storage.save_order.call_args[0]
        assert saved_data["item_name"] == "Laptop"
        assert saved_data["quantity"] == 2
        assert saved_data["customer_id"] == "CUST99"
        assert saved_data["order_id"] == "O1"

    def test_accepts_explicit_valid_status(self, order_tracker, mock_storage):
        order_tracker.add_order("O1", "Laptop", 1, "C1", status="shipped")
        _, saved_data = mock_storage.save_order.call_args[0]
        assert saved_data["status"] == "shipped"

    def test_raises_for_duplicate_id(self, order_tracker, mock_storage):
        mock_storage.get_order.return_value = {"order_id": "DUP"}
        with pytest.raises(ValueError, match="already exists"):
            order_tracker.add_order("DUP", "Item", 1, "C1")

    def test_raises_for_zero_quantity(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="quantity"):
            order_tracker.add_order("O1", "Item", 0, "C1")

    def test_raises_for_negative_quantity(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="quantity"):
            order_tracker.add_order("O1", "Item", -3, "C1")

    def test_raises_for_empty_order_id(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="order_id"):
            order_tracker.add_order("", "Item", 1, "C1")

    def test_raises_for_empty_item_name(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="item_name"):
            order_tracker.add_order("O1", "", 1, "C1")

    def test_raises_for_empty_customer_id(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="customer_id"):
            order_tracker.add_order("O1", "Item", 1, "")

    def test_raises_for_invalid_initial_status(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="status"):
            order_tracker.add_order("O1", "Item", 1, "C1", status="flying")


# --- get_order_by_id ---

class TestGetOrderById:
    def test_returns_none_when_not_found(self, order_tracker, mock_storage):
        assert order_tracker.get_order_by_id("MISSING") is None

    def test_returns_order_when_found(self, order_tracker, mock_storage):
        mock_storage.get_order.return_value = {"order_id": "O1", "status": "pending"}
        result = order_tracker.get_order_by_id("O1")
        assert result["order_id"] == "O1"

    def test_delegates_to_storage(self, order_tracker, mock_storage):
        order_tracker.get_order_by_id("O1")
        mock_storage.get_order.assert_called_once_with("O1")

    def test_raises_for_empty_id(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="order_id"):
            order_tracker.get_order_by_id("")


# --- update_order_status ---

class TestUpdateOrderStatus:
    def test_saves_new_status(self, order_tracker, mock_storage):
        mock_storage.get_order.return_value = {"order_id": "O1", "status": "pending"}
        order_tracker.update_order_status("O1", "shipped")
        _, saved_data = mock_storage.save_order.call_args[0]
        assert saved_data["status"] == "shipped"

    def test_preserves_other_fields(self, order_tracker, mock_storage):
        mock_storage.get_order.return_value = {
            "order_id": "O1", "item_name": "Laptop", "quantity": 1,
            "customer_id": "C1", "status": "pending"
        }
        order_tracker.update_order_status("O1", "shipped")
        _, saved_data = mock_storage.save_order.call_args[0]
        assert saved_data["item_name"] == "Laptop"

    def test_raises_for_nonexistent_order(self, order_tracker, mock_storage):
        mock_storage.get_order.return_value = None
        with pytest.raises(ValueError, match="not found"):
            order_tracker.update_order_status("MISSING", "shipped")

    def test_raises_for_invalid_status_without_reading_storage(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="status"):
            order_tracker.update_order_status("O1", "flying")
        mock_storage.get_order.assert_not_called()

    def test_raises_for_empty_id(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="order_id"):
            order_tracker.update_order_status("", "shipped")


# --- list_all_orders ---

class TestListAllOrders:
    def test_returns_empty_list_when_no_orders(self, order_tracker, mock_storage):
        assert order_tracker.list_all_orders() == []

    def test_returns_all_orders(self, order_tracker, mock_storage):
        mock_storage.get_all_orders.return_value = {
            "O1": {"order_id": "O1", "status": "pending"},
            "O2": {"order_id": "O2", "status": "shipped"},
        }
        assert len(order_tracker.list_all_orders()) == 2


# --- list_orders_by_status ---

class TestListOrdersByStatus:
    def test_returns_only_matching_status(self, order_tracker, mock_storage):
        mock_storage.get_all_orders.return_value = {
            "O1": {"order_id": "O1", "status": "pending"},
            "O2": {"order_id": "O2", "status": "shipped"},
        }
        result = order_tracker.list_orders_by_status("pending")
        assert len(result) == 1
        assert result[0]["order_id"] == "O1"

    def test_returns_empty_when_none_match(self, order_tracker, mock_storage):
        mock_storage.get_all_orders.return_value = {
            "O1": {"order_id": "O1", "status": "pending"},
        }
        assert order_tracker.list_orders_by_status("delivered") == []

    def test_returns_empty_list_when_storage_empty(self, order_tracker, mock_storage):
        assert order_tracker.list_orders_by_status("pending") == []

    def test_raises_for_empty_status(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="status"):
            order_tracker.list_orders_by_status("")

    def test_raises_for_invalid_status(self, order_tracker, mock_storage):
        with pytest.raises(ValueError, match="status"):
            order_tracker.list_orders_by_status("flying")
