import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from razorpay.errors import BadRequestError, GatewayError, ServerError

from myapp.razorpay_integration import (
    start_razorpay_txn,
    update_transaction_details,
    capture_transaction,
    refund_transaction,
    validate_signature,
    create_razorpay_order,
    RazorpayError
)

from myapp.models import RazorpayTransaction as Transaction


@pytest.fixture
def mock_basket():
    class Basket:
        id = 1
        currency = 'INR'
    return Basket()


@pytest.fixture
def mock_user():
    class User:
        id = 1
    return User()


@pytest.fixture
def mock_transaction(mock_basket, mock_user):
    return start_razorpay_txn(mock_basket, Decimal('100.00'), user=mock_user, email='test@example.com')


def test_start_razorpay_txn(mock_basket, mock_user):
    txn = start_razorpay_txn(mock_basket, Decimal('100.00'), mock_user, 'test@example.com')
    assert txn.amount == Decimal('100.00')
    assert txn.currency == 'INR'
    assert txn.basket_id == mock_basket.id
    assert txn.email == 'test@example.com'


@patch('myapp.razorpay_integration.rz_client.payment.fetch')
def test_update_transaction_details(mock_fetch, mock_transaction):
    mock_fetch.return_value = {
        'amount': 10000,
        'currency': 'INR',
        'status': 'captured',
        'method': 'card'
    }
    txn = update_transaction_details('rz_payment_id_123', mock_transaction.txnid)
    assert txn.status == 'captured'
    assert txn.rz_id == 'rz_payment_id_123'


@patch('myapp.razorpay_integration.rz_client.payment.fetch')
def test_capture_transaction(mock_fetch, mock_transaction):
    mock_transaction.rz_id = 'rz_payment_id_123'
    mock_transaction.save()
    mock_fetch.return_value = {'status': 'captured'}
    txn = capture_transaction(mock_transaction.rz_id)
    assert txn.status == 'captured'


@patch('myapp.razorpay_integration.rz_client.payment.refund')
def test_refund_transaction(mock_refund, mock_transaction):
    mock_transaction.rz_id = 'rz_payment_id_123'
    mock_transaction.save()
    refund_transaction(mock_transaction.rz_id, 10000, 'INR')
    mock_refund.assert_called_once()


@patch('myapp.razorpay_integration.rz_client.utility.verify_payment_signature')
def test_validate_signature_success(mock_verify):
    mock_verify.return_value = True
    result = validate_signature('order_123', 'payment_123', 'sig_123')
    assert result is True


@patch('myapp.razorpay_integration.rz_client.utility.verify_payment_signature', side_effect=BadRequestError('Bad Request'))
def test_validate_signature_failure(mock_verify):
    with pytest.raises(RazorpayError):
        validate_signature('order_123', 'payment_123', 'sig_123')


@patch('myapp.razorpay_integration.rz_client.order.create')
def test_create_razorpay_order(mock_create, mock_basket, mock_transaction):
    mock_create.return_value = {'id': 'order_123'}
    order = create_razorpay_order(Decimal('100.00'), mock_basket, mock_transaction)
    assert order['id'] == 'order_123'


def test_create_razorpay_order_invalid_amount(mock_basket, mock_transaction):
    with pytest.raises(ValueError):
        create_razorpay_order('invalid', mock_basket, mock_transaction)
