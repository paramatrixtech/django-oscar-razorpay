import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist

from rzpay.models import RazorpayTransaction
from rzpay.facade import (
    start_razorpay_txn, update_transaction_details, capture_transaction,
    refund_transaction, validate_signature, create_razorpay_order, RazorpayError
)
import razorpay

@pytest.fixture
def basket():
    return MagicMock(id=1, currency='INR')

@pytest.fixture
def user():
    return MagicMock(id=2)

@pytest.fixture
def transaction():
    txn = RazorpayTransaction(
        txnid="testtxnid",
        amount=Decimal("99.99"),
        currency="INR",
        basket_id=1
    )
    txn.save()
    return txn

@patch('django_oscar_razorpay.rzpay.facade.Transaction')
def test_start_razorpay_txn(mock_txn, basket, user):
    instance = MagicMock()
    mock_txn.return_value = instance
    result = start_razorpay_txn(basket, Decimal("99.99"), user=user, email="test@example.com")
    assert instance.save.called
    assert result == instance


@patch('django_oscar_razorpay.rzpay.facade.Transaction')
def test_start_razorpay_txn_failure(mock_txn, basket, user):
    mock_txn.side_effect = Exception("DB error")

    try:
        start_razorpay_txn(basket, Decimal("99.99"), user=user, email="test@example.com")
    except RazorpayError as e:
        print(f"Caught RazorpayError: {e}")
        assert "Failed to create Razorpay transaction" in str(e)


@pytest.mark.django_db
@patch('django_oscar_razorpay.rzpay.facade.rz_client')
@patch('django_oscar_razorpay.rzpay.facade.Transaction.objects.get')
def test_update_transaction_details_success(mock_get, mock_client, transaction):
    mock_payment = {
        "amount": int(transaction.amount * 100),
        "currency": transaction.currency,
        "status": "captured",
        "method": "card"
    }
    mock_client.payment.fetch.return_value = mock_payment
    mock_get.return_value = transaction

    updated_txn = update_transaction_details("rz_payment_id", transaction.txnid)
    assert updated_txn.status == "captured"
    assert updated_txn.payment_mode == "card"

@pytest.mark.django_db
@patch('django_oscar_razorpay.rzpay.facade.rz_client')
@patch('django_oscar_razorpay.rzpay.facade.Transaction.objects.get')
def test_update_transaction_details_failure(mock_get, mock_client, transaction):
    mock_client.payment.fetch.side_effect = razorpay.errors.BadRequestError({}, "Invalid ID")
    mock_get.return_value = transaction

    with pytest.raises(RazorpayError):
        update_transaction_details("invalid_id", transaction.txnid)

@pytest.mark.django_db
@patch('django_oscar_razorpay.rzpay.facade.Transaction.objects.get')
@patch('django_oscar_razorpay.rzpay.facade.rz_client')
def test_capture_transaction(mock_client, mock_get, transaction):
    mock_get.return_value = transaction
    mock_client.payment.fetch.return_value = {"status": "captured"}
    txn = capture_transaction("rz_payment_id")
    assert txn.status == "captured"

@pytest.mark.django_db
@patch('django_oscar_razorpay.rzpay.facade.Transaction.objects.get')
@patch('django_oscar_razorpay.rzpay.facade.rz_client')
def test_capture_transaction_txn_not_found(mock_client, mock_get):
    mock_get.side_effect = RazorpayTransaction.DoesNotExist

    with pytest.raises(RazorpayError):
        capture_transaction("missing_payment_id")

@pytest.mark.django_db
@patch('django_oscar_razorpay.rzpay.facade.Transaction.objects.get')
@patch('django_oscar_razorpay.rzpay.facade.rz_client')
def test_refund_transaction_success(mock_client, mock_get, transaction):
    mock_get.return_value = transaction
    refund_transaction("rz_payment_id", int(transaction.amount * 100), transaction.currency)
    mock_client.payment.refund.assert_called_once()

@pytest.mark.django_db
@patch('django_oscar_razorpay.rzpay.facade.Transaction.objects.get')
@patch('django_oscar_razorpay.rzpay.facade.rz_client')
def test_refund_transaction_failure(mock_client, mock_get, transaction):
    mock_get.return_value = transaction
    mock_client.payment.refund.side_effect = razorpay.errors.ServerError({}, "Refund failed")

    with pytest.raises(RazorpayError):
        refund_transaction("rz_payment_id", int(transaction.amount * 100), transaction.currency)

@patch('django_oscar_razorpay.rzpay.facade.rz_client')
def test_validate_signature_success(mock_client):
    mock_client.utility.verify_payment_signature.return_value = True
    assert validate_signature("order_id", "payment_id", "signature") is True

@patch('django_oscar_razorpay.rzpay.facade.rz_client')
def test_validate_signature_fail(mock_client):
    mock_client.utility.verify_payment_signature.side_effect = razorpay.errors.SignatureVerificationError()
    with pytest.raises(RazorpayError):
        validate_signature("order_id", "payment_id", "invalid_signature")

@pytest.mark.django_db
@patch('django_oscar_razorpay.rzpay.facade.rz_client')
def test_create_razorpay_order_success(mock_client, basket, transaction):
    mock_order = {'id': 'order_1234'}
    mock_client.order.create.return_value = mock_order
    result = create_razorpay_order(99.99, basket, transaction)
    assert result['id'] == 'order_1234'
    
@pytest.mark.django_db
@patch('django_oscar_razorpay.rzpay.facade.rz_client')
def test_create_razorpay_order_failure(mock_client, basket, transaction):
    mock_client.order.create.side_effect = razorpay.errors.BadRequestError({}, "Invalid Order")

    with pytest.raises(RazorpayError):
        create_razorpay_order(99.99, basket, transaction)

