import datetime
import requests
from account.models import IDCard
from api.utils.response.response_format import bad_request_response, success_response
from transaction.models import Transaction

class Paystack:
    """
    Paystack class to handle payment-related tasks such as
    initiating transactions and verifying payments.
    """

    @staticmethod
    def get_header():
        headers = {
            "Authorization": f"Bearer sk_test_f2c4c12c87df60bc178d3be7a19ba4a975d17527",
            "Content-Type": "application/json"
        }
        return headers

    @staticmethod
    def charge_user(request,user_id, transaction_type, **kwargs):
        transaction=None
        try:
            amount = 50000  # Example amount (in kobo)
            redirect_url = f"{request.data.get('redirect_url')}"

            # Create transaction record in database
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount / 100,
                transaction_type=transaction_type,
                status="pending",
            )
            metadata = {
                "application_id": str(transaction.id),
                "email": transaction.user.email,
                "description": "Payment for NIN Enrolment"
            }

            # Prepare request payload for Paystack
            data = {
                "email": transaction.user.email,
                "amount": amount, 
                "reference":str(transaction.id),
                "currency": "NGN",
                "callback_url": redirect_url,
                "metadata": metadata,
            }

            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                json=data,
                headers=Paystack.get_header()
            )

            if response.ok:
                response_data = response.json()
                if response.status_code == 200 and response_data["status"] == True:
                    print(response_data['data'])
                    payment_url = response_data['data']['authorization_url']
                    return success_response(
                        data={"payment_url": payment_url},
                    )

                return bad_request_response(message=response_data.get('message', 'Failed to initiate payment.'))

            return bad_request_response(message='Failed to initiate payment.')

        except Exception as e:
            return bad_request_response(message=str(e))
        

    
    @staticmethod
    def charge_user_for_donation(request,amount, name, email=None):
        try:
            amount = float(amount) * 100  # amount (in kobo)
            redirect_url = f"{request.data.get('redirect_url')}"

            print(amount)
            print(amount)
            print(amount)
            metadata = {
                "payment_mode": 'donation',
                "name": name,
                "email": email,
                "description": "Donation"
            }

            # Prepare request payload for Paystack
            data = {
                "email": email,
                "amount": amount, 
                "currency": "NGN",
                "callback_url": redirect_url,
                "metadata": metadata,
            }

            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                json=data,
                headers=Paystack.get_header()
            )
            print(response.text) 
            if response.ok:
                response_data = response.json()
                if response.status_code == 200 and response_data["status"] == True:
                    print(response_data['data'])
                    payment_url = response_data['data']['authorization_url']
                    return success_response(
                        data={"payment_url": payment_url},
                    )

                return bad_request_response(message=response_data.get('message', 'Failed to initiate payment.'))

            return bad_request_response(message='Failed to initiate payment.')

        except Exception as e:
            return bad_request_response(message=str(e))


    @staticmethod
    def validate_payment(transaction_id):
        try:
            # Verify payment with Paystack
            response = requests.get(
                f"https://api.paystack.co/transaction/verify/{transaction_id}",
                headers=Paystack.get_header()
            )
            if response.ok:
                response_data = response.json()
                # print(response_data)
                if response.status_code == 200 and response_data["status"] in ["success",True]:
                    payment_status = response_data['data']['status']
                    system_tx_ref = response_data['data']['reference']
                    
                    try:
                        transaction = Transaction.objects.get(id=system_tx_ref)
                    except:
                        return bad_request_response(
                            message="Transaction not found."
                        )

                    # Update the transaction based on the payment status
                    if payment_status == "success":
                        if transaction.status == 'success':
                            return success_response(
                                message="Transaction already successful.",
                                data={
                                    "transaction_id": str(transaction.id),
                                    "success":True,
                                    "amount": transaction.amount,
                                    "message": "Transaction already successful."
                                }
                            )
                        if transaction.status != "success":
                            transaction.status = "success"
                            transaction.response = response_data['data']
                            id_card, created = IDCard.objects.get_or_create(user=transaction.user)
                            id_card.is_active =True
                            id_card.first_time =False
                            id_card.expired = False
                            # let expired at 30 days from today
                            id_card.expired_at = datetime.date.today() + datetime.timedelta(days=30)
                            id_card.save()
                            transaction.save()
                            return success_response(
                                message="Payment successful.",
                                data={
                                    "transaction_id": str(transaction.id),
                                    "success":True,
                                    "amount": transaction.amount,
                                    "message": "Payment successful."
                                }
                            )
                  
                        return success_response(message="Payment successful.")

                    elif payment_status == "failed":
                        transaction.status = "failed"
                        transaction.response = response_data['data']
                        transaction.save()
                        return bad_request_response(message="Payment not successful.")
                    else:
                        return bad_request_response(message='Payment still processing')

                return bad_request_response(message="Payment verification failed.")

            return bad_request_response(message='Failed to verify payment.')

        except Transaction.DoesNotExist:
            return bad_request_response(message="Transaction not found.")
        except Exception as e:
            print(e)
            return bad_request_response(message='Unable to verify payment at the moment')
        

    @staticmethod
    def validate_payment_donation(transaction_id):
        try:
            # Verify payment with Paystack
            response = requests.get(
                f"https://api.paystack.co/transaction/verify/{transaction_id}",
                headers=Paystack.get_header()
            )
            if response.ok:
                response_data = response.json()
                if response.status_code == 200 and response_data["status"] in ["success",True]:

                    return success_response(
                                message="Transaction already successful.",
                    )
                return bad_request_response(message="Payment verification failed.")
            return bad_request_response(message='Failed to verify payment.')
        except Transaction.DoesNotExist:
            return bad_request_response(message="Transaction not found.")
        except Exception as e:
            print(e)
            return bad_request_response(message='Unable to verify payment at the moment')
        


    @staticmethod
    def process_webhook(payload):
        try:
            transaction_id = payload['data']['reference']
            payment_status = payload['data']['status']

            # Call Paystack to verify the payment
            response = requests.get(
                f"https://api.paystack.co/transaction/verify/{transaction_id}",
                headers=Paystack.get_header()
            )

            if response.ok:
                response_data = response.json()
                if response.status_code == 200 and response_data["status"] == "success":
                    payment_status = response_data['data']['status']
                    system_tx_ref = response_data['data']['reference']

                    transaction = Transaction.objects.get(id=system_tx_ref)

                    # Update the transaction based on the payment status
                    if payment_status == "success":
                        if transaction.status == 'success':
                            return success_response(
                                message="Transaction already successful.",
                                data={"message": "Transaction already successful."}
                            )
                        if transaction.status != "success":
                            transaction.status = "success"
                            transaction.response = response_data['data']
                            id_card, created = IDCard.objects.get_or_create(user=transaction.user)
                            id_card.is_active =True
                            id_card.expired = False
                            # let expired at 30 days from today
                            id_card.expired_at = datetime.date.today() + datetime.timedelta(days=30)
                            id_card.save()
                            transaction.save()
                            return success_response(
                                message="Payment successful.",
                                data={
                                    "transaction_id": str(transaction.id),
                                    "amount": transaction.amount,
                                    "message": "Payment successful."
                                }
                            )
                  
                        return success_response(message="Payment successful.")

                    elif payment_status == "failed":
                        transaction.status = "failed"
                        transaction.response = response_data['data']
                        transaction.save()
                        return bad_request_response(message="Payment not successful.")
                    else:
                        return bad_request_response(message='Payment still processing')

                return bad_request_response(message="Payment verification failed.")

            return bad_request_response(message='Failed to verify payment.')

        except Transaction.DoesNotExist:
            return bad_request_response(message="Transaction not found.")
        except Exception as e:
            return bad_request_response(message=str(e))

