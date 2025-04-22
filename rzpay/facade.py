"""
Responsible for briding between Oscar and the Razorpay gateway
"""
import logging
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import razorpay.errors

from .models import RazorpayTransaction as Transaction
from .exceptions import RazorpayError
from decimal import Decimal, InvalidOperation

import razorpay

# Initialize the Razorpay client with API credentials
rz_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET)
)

logger = logging.getLogger('razorpay')


def start_razorpay_txn(basket, amount, user=None, email=None):
    """
    Record the start of a transaction and calculate costs, etc.
    """
    currency = basket.currency or getattr(settings,
                                          'OSCAR_DEFAULT_CURRENCY',
                                          'INR')

    # Create a new transaction record
    transaction = Transaction(
        user=user,
        amount=amount,
        currency=currency,
        basket_id=basket.id,
        txnid=uuid4().hex[:28],  # Generate a unique transaction ID
        email=email
    )
    transaction.save()

    logger.info(f"Started Razorpay transaction {transaction.txnid} for basket \
        {basket.id} with amount {amount} {currency}")

    return transaction


def update_transaction_details(rz_payment_id, txn_id):
    """
    Fetch the completed details about the Razorpay transaction and update our
    transaction model.
    """
    try:
        # Fetch payment details from Razorpay
        payment = rz_client.payment.fetch(rz_payment_id)
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Bad request error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Failed to create Razorpay order: {str(e)}")
    except razorpay.errors.GatewayError as e:
        logger.error(f"Gateway error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay gateway error: {str(e)}")
    except razorpay.errors.ServerError as e:
        logger.error(f"Server error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay server error: {str(e)}")
    except Exception as e:
        logger.warning(f"Unable to fetch transaction details for Razorpay txn \
            {rz_payment_id}: {e}")
        raise RazorpayError("Failed to fetch transaction details from Razorpay")  # noqa

    try:
        # Fetch the corresponding transaction from the database
        txn = Transaction.objects.get(txnid=txn_id)
    except ObjectDoesNotExist as e:
        logger.warning(f"Unable to find transaction details for txnid \
            {txn_id}: {e}")
        raise RazorpayError("Transaction not found in the database")

    # Ensure amount and currency match between the Razorpay payment and our \
        # transaction record
    expected_amount = int(txn.amount * 100)
    actual_amount = payment["amount"]
    expected_currency = txn.currency
    actual_currency = payment["currency"]
    if expected_amount != actual_amount or expected_currency != actual_currency:  # noqa
        logger.warning(
            f"Payment details mismatch for txn {txn.txnid} and Razorpay payment {rz_payment_id}. "  # noqa
            f"Expected amount: {expected_amount}, Actual amount: {actual_amount}. "  # noqa
            f"Expected currency: '{expected_currency}', Actual currency: '{actual_currency}'."  # noqa
        )
        raise RazorpayError("Transaction details mismatch")

    # Update the transaction status and Razorpay ID
    txn.status = payment["status"]
    txn.rz_id = rz_payment_id
    txn.payment_mode = payment["method"]
    txn.save()

    logger.info(f"Updated transaction {txn.txnid} with status {txn.status}")

    return txn


def capture_transaction(rz_payment_id):
    """
    Capture the payment for a given Razorpay transaction ID.
    """
    try:
        # Fetch the transaction from the database
        txn = Transaction.objects.get(rz_id=rz_payment_id)

        # Capture the payment via Razorpay
        if rz_client.payment.fetch(rz_payment_id)["status"] == "captured":
            # Update the transaction status to "captured"
            txn.status = "captured"
            txn.save()

        logger.info(f"Captured payment for transaction {txn.txnid}")
    except ObjectDoesNotExist:
        logger.error(f"Transaction with Razorpay ID {rz_payment_id} not found")
        raise RazorpayError("Transaction not found")
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Bad request error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Failed to create Razorpay order: {str(e)}")
    except razorpay.errors.GatewayError as e:
        logger.error(f"Gateway error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay gateway error: {str(e)}")
    except razorpay.errors.ServerError as e:
        logger.error(f"Server error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay server error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while capturing payment for \
            transaction {txn.txnid}: {e}")
        raise RazorpayError(f"Error capturing payment for {txn.txnid}")

    return txn


def refund_transaction(rz_payment_id, amount, currency):
    """
    Refund a given amount of the payment for a specific Razorpay transaction.
    """
    try:
        # Fetch the transaction from the database
        txn = Transaction.objects.get(rz_id=rz_payment_id)

        # Ensure the refund amount is less than or equal to the \
        # transaction amount
        if amount > int(txn.amount * 100):
            raise RazorpayError("Refund amount exceeds the original \
                transaction amount")

        # Ensure the currency matches the original transaction currency
        if currency != txn.currency:
            raise RazorpayError("Currency mismatch for the refund")

        # Initiate the refund via Razorpay
        rz_client.payment.refund(rz_payment_id, amount)

        logger.info(f"Refunded {amount / 100:.2f} {currency} for transaction \
            {txn.txnid}")

    except ObjectDoesNotExist:
        logger.error(f"Transaction with Razorpay ID {rz_payment_id} not found")
        raise RazorpayError("Transaction not found")
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Bad request error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Failed to create Razorpay order: {str(e)}")
    except razorpay.errors.GatewayError as e:
        logger.error(f"Gateway error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay gateway error: {str(e)}")
    except razorpay.errors.ServerError as e:
        logger.error(f"Server error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay server error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while refunding transaction \
            {rz_payment_id}: {e}")
        raise RazorpayError(f"Error refunding transaction {rz_payment_id}")


def validate_signature(rz_order_id: str, rz_payment_id: str,
                       rz_signature: str) -> bool:
    """
    Validates the Razorpay payment signature to ensure the transaction is \
        legitimate.

    Args:
        rz_order_id (str): The Razorpay order ID.
        rz_payment_id (str): The Razorpay payment ID.
        rz_signature (str): The Razorpay signature to verify.

    Returns:
        bool: True if the signature is valid.

    Raises:
        RazorpayError: If the signature verification fails or if there is an \
            error with the Razorpay SDK.
        ValueError: If any of the input parameters are missing or invalid.
    """
    # Input validation
    if not all([rz_order_id, rz_payment_id, rz_signature]):
        raise ValueError("Missing required parameters: order ID, payment ID, \
            or signature")

    try:
        # Prepare the signature data for verification
        rz_signature_data = {
            'razorpay_order_id': rz_order_id,
            'razorpay_payment_id': rz_payment_id,
            'razorpay_signature': rz_signature
        }

        # Verify the payment signature using Razorpay's utility
        rz_client.utility.verify_payment_signature(rz_signature_data)
        return True

    except razorpay.errors.SignatureVerificationError:
        raise RazorpayError(f"Signature verification failed for payment ID: \
            {rz_payment_id}")
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Bad request error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Failed to create Razorpay order: {str(e)}")
    except razorpay.errors.GatewayError as e:
        logger.error(f"Gateway error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay gateway error: {str(e)}")
    except razorpay.errors.ServerError as e:
        logger.error(f"Server error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay server error: {str(e)}")
    except Exception as e:
        raise RazorpayError(f"Error verifying signature for payment ID: \
            {rz_payment_id}. Details: {str(e)}")
    

def create_razorpay_order(amount, basket, txn):
    """
    Creates a Razorpay order for the given amount, currency, and \
        transaction ID.

    Args:
        amount (float): The amount to charge (in the base currency, e.g., INR).
        basket (Any): The basket object containing currency information.
        txn (Any): The transaction object containing the transaction ID \
            (txnid).

    Returns:
        Dict[str, Any]: The created Razorpay order details.

    Raises:
        RazorpayError: If there is an error creating the Razorpay order.
        ValueError: If any of the input parameters are invalid.
    """
    # Input validation
    try:
        decimal_amount = Decimal(str(amount))  # Convert to Decimal
        if decimal_amount <= 0:
            raise ValueError("Amount must be a positive decimal number")
    except (InvalidOperation, TypeError):
        raise ValueError("Invalid amount: must be a valid decimal number")

    if not hasattr(txn, 'txnid') or not txn.txnid:
        raise ValueError("Transaction ID (txnid) is required and cannot be \
            empty")

    # Determine the currency (fallback to settings or default to INR)
    currency = basket.currency or getattr(settings, 'OSCAR_DEFAULT_CURRENCY')

    # Convert amount to paise (or smallest unit for the currency)
    # Note: For INR, Razorpay expects the amount in paise (1 INR = 100 paise)
    amount_in_paise = int(amount * 100)

    try:
        # Create the Razorpay order
        order_data = {
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": txn.txnid
        }
        rz_order = rz_client.order.create(order_data)

        logger.info(f"Razorpay order created successfully: {rz_order['id']}")
        return rz_order

    except razorpay.errors.BadRequestError as e:
        logger.error(f"Bad request error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Failed to create Razorpay order: {str(e)}")
    except razorpay.errors.GatewayError as e:
        logger.error(f"Gateway error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay gateway error: {str(e)}")
    except razorpay.errors.ServerError as e:
        logger.error(f"Server error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Razorpay server error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating Razorpay order: {str(e)}")
        raise RazorpayError(f"Unexpected error creating Razorpay order: {str(e)}")