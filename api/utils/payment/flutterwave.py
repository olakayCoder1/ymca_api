import logging, requests
import traceback
from django.conf import settings
from account.models import CodeConfirmation, User
from billing.models import Transaction
from helper.utils.email.send_mail import Email
from helper.utils.location.printscan import PrintScan
from helper.utils.response.response_format import bad_request_response, success_response , internal_server_error_response
from identity.models.application import NationalIdentificationNumberApplication



class Flutterwave:
    """
    Flutterwave class that handles user payment via Flutterwave.
    """

    @staticmethod
    def get_header():
        headers = {
                "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        return headers

    @staticmethod
    def charge_user(request,application:NationalIdentificationNumberApplication, *args, **kwargs):
        transaction = None
        try:
            amount = 50  # Amount for the payment (in dollars)

            transaction = Transaction.objects.create(
                user=kwargs.get("auth_user"),
                amount=amount,
                application=application,
                payment_status="PENDING",
                payment_provider="FLUTTERWAVE",
            )

            # Define metadata
            metadata = {
                "application_id": str(application.id),
                "email": application.email,
                "description": "Payment for NIN Enrolment"
            }

            redirect_url = f"{request.data.get('redirect_url')}&payment_type={transaction.payment_provider}"


            data = {
                "tx_ref": f"{transaction.id}",
                "amount": amount,
                "currency": "NGN",
                "redirect_url": redirect_url,
                "payment_type": "card",
                "customer": {
                    "email": application.email,
                    "name": f"{application.first_name} {application.last_name}",
                },
                "meta": metadata,  
                "customizations": {
                    "title": "NIN Enrolment Payment",
                    "description": "Payment for NIN Enrolment"
                }
            }

            response = requests.post(
                "https://api.flutterwave.com/v3/payments",
                json=data,
                headers=Flutterwave.get_header()
            )
            if response.ok:
                response_data = response.json()

                if response.status_code == 200 and response_data["status"] == "success":
                    payment_url = response_data['data']['link']
                    return success_response(data={
                        "payment_url": payment_url,
                        "transaction_id": str(transaction.id),
                    })
                
                transaction.delete()
                return bad_request_response(message=response_data.get('message', 'Failed to initiate payment.'))
            
            transaction.delete()
            return bad_request_response(message='Failed to initiate payment.')

        except Exception as e:
            if transaction:transaction.delete()
            logging.error(e)
            logging.error(traceback.print_exc())
            return bad_request_response(message=str(e))
        


        
    @staticmethod
    def validate_payment(request,transaction_id,redirect_url):
        try:
            # Call Flutterwave's API to verify the payment
            response = requests.get(
                f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify",
                headers=Flutterwave.get_header()
            )

            if response.ok:
                response_data = response.json()
                if response.status_code == 200 and response_data["status"] == "success":
                    payment_status = response_data['data']['status']
                    system_tx_ref = response_data['data']['tx_ref']

                    transaction = Transaction.objects.get(id=system_tx_ref)

                    # Update the transaction based on the payment status
                    if payment_status == "successful":
                        if transaction.payment_status != "SUCCESS":
                            payment_type = transaction.payment_type
                            if payment_type == "NIN":
                                try:
                                    application_record = NationalIdentificationNumberApplication.objects.get(id=transaction.application.id)
                                    application_record.payment_status = "PAID"
                                    application_record.application_status = "SUBMITTED"
                                    transaction.payment_status = "SUCCESS"
                                    transaction.payment_reference = transaction_id
                                    transaction.response = response_data['data']
                                    transaction.save()


                                    # if not application_record.capturing_order_comfirmed:
                                    #     success , printscan_response = PrintScan().submit_appointment_order(
                                    #         tracking_id_tcn=application_record.capturing_order_ref,
                                    #         tracking_id_tcr=application_record.capturing_order_ref,
                                    #     )
                                    #     if success:
                                    #         application_record.capturing_order_comfirmed = True
                                                
                                    application_record.save()

                                    if application_record.is_create_account:
                                        try:
                                            
                                            try:
                                                new_user = User.objects.get(email=application_record.email)
                                                new_user.first_name = application_record.first_name
                                                new_user.last_name = application_record.last_name
                                                new_user.save()
                                            except:
                                                new_user = User.objects.create(
                                                    first_name=application_record.first_name,
                                                    last_name=application_record.last_name,
                                                    email=application_record.email
                                                )

                                            try:
                                                # code = CodeConfirmation.generate_unique_code()
                                                # CodeConfirmation.objects.create(
                                                #     user=new_user,
                                                #     code=code,   
                                                #     confirmation_type='registration'
                                                # )
                                                
                                                # redirect_url = f"{redirect_url}?code={code}"
                                                # # send account setup email
                                                # Email.send_account_setup_notification(
                                                #     new_user.email,
                                                #     redirect_url,
                                                #     f"{new_user.first_name} {new_user.last_name}"
                                                # )
                                                pass
                                            except:pass


                                            try:
                                                success , printscan_response = PrintScan().get_single_location(location_id=application_record.capturing_location_id)
                                                if success:
                                                    Email.send_capturing_location_detail(
                                                        email=application_record.email,
                                                        name=application_record.first_name, 
                                                        center_name=printscan_response.get('name'),
                                                        capturing_reference=application_record.capturing_order_ref,
                                                        city=printscan_response.get('city'),
                                                        state=printscan_response.get('state'),
                                                        address_1=printscan_response.get('address1'),
                                                        address_2=printscan_response.get('address2'),
                                                        capturing_date=application_record.capturing_date.date() if application_record.capturing_date else None,
                                                        application_ref="",
                                                        capturing_time=application_record.capturing_date.time() if application_record.capturing_date else None 
                                                    )

                                            except:pass
                                        except:pass


                                    # Email.send_access_code_notification(application_record.email,code=application_record.code,name=application_record.first_name)
                                    return success_response(message="Payment successful.")
                                except NationalIdentificationNumberApplication.DoesNotExist:
                                    return bad_request_response(message="Invalid payment type")
                            else:return bad_request_response(message="Invalid payment type")

                        return success_response(message="Payment successful.")
                    elif payment_status == "failed":
                        transaction.payment_status = "FAILED"
                        transaction.payment_reference = transaction_id
                        transaction.response = response_data['data']
                        transaction.save()
                        return bad_request_response(message="Payment not successful.")
                    else:
                        return bad_request_response(message='Payment still processing')

    
                else:
                    return bad_request_response(message="Payment not successful.")
                
                
            return bad_request_response(message='Failed to validate payment.')


        except Transaction.DoesNotExist:
            return bad_request_response(message="Transaction not found.")
        
        except Exception as e:
            return internal_server_error_response()
        



    @staticmethod
    def process_webhook(payload):
        transaction_id = payload['data']['id']
        payment_status = payload['data']['status']
        
        # Retrieve transaction using the flutterwave payment id
        try:
            # Call Flutterwave's API to verify the payment
            response = requests.get(
                f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify",
                headers=Flutterwave.get_header()
            )


            if response.ok:
                response_data = response.json()
                if response.status_code == 200 and response_data["status"] == "success":
                    payment_status = response_data['data']['status']
                    system_tx_ref = response_data['data']['tx_ref']

                    transaction = Transaction.objects.get(id=system_tx_ref)

                    # Update the transaction based on the payment status
                    if payment_status in ["successful","SUCCESSFUL"]:
                        if transaction.payment_status != "SUCCESS":
                            payment_type = transaction.payment_type
                            if payment_type == "NIN":
                                try:
                                    application_record = NationalIdentificationNumberApplication.objects.get(id=transaction.application.id)
                                    application_record.payment_status = "PAID"
                                    application_record.application_status = "SUBMITTED"
                                    transaction.payment_status = "SUCCESS"
                                    transaction.payment_reference = transaction_id
                                    transaction.response = response_data['data']
                                    transaction.save()
                                    application_record.save()

                                    if application_record.is_create_account:
                                        try:
                                            new_user = User.objects.create(
                                                first_name=application_record.first_name,
                                                last_name=application_record.last_name,
                                                email=application_record.email
                                            )

                                            code = CodeConfirmation.generate_unique_code()
                                            CodeConfirmation.objects.create(
                                                user=new_user,
                                                code=code,   
                                                confirmation_type='registration'
                                            )
                                            
                                            redirect_url = f"{redirect_url}?code={code}"
                                            # send account setup email
                                            Email.send_account_setup_notification(
                                                new_user.email,
                                                redirect_url,
                                                f"{new_user.first_name} {new_user.last_name}"
                                            )
                                        except:pass


                                    Email.send_access_code_notification(application_record.email,code=application_record.code,name=application_record.first_name)
                                    return success_response(message="Payment successful.")
                                except NationalIdentificationNumberApplication.DoesNotExist:
                                    return bad_request_response(message="Invalid payment type")
                            else:return bad_request_response(message="Invalid payment type")

                        return success_response(message="Payment successful.")
                    elif payment_status == "failed":
                        transaction.payment_status = "FAILED"
                        transaction.payment_reference = transaction_id
                        transaction.response = response_data['data']
                        transaction.save()
                        return bad_request_response(message="Payment not successful.")
                    else:
                        return bad_request_response(message='Payment still processing')

    
                else:
                    return bad_request_response(message="Payment not successful.")
                
                
            return bad_request_response(message='Failed to validate payment.')

            
        except Transaction.DoesNotExist:
            pass