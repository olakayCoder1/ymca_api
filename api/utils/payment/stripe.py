from account.models import CodeConfirmation, User
from billing.models import Transaction
import stripe
import logging
import traceback
import requests
from django.conf import settings
from helper.utils.email.send_mail import Email
from helper.utils.location.printscan import PrintScan
from helper.utils.response.response_format import internal_server_error_response, success_response , bad_request_response, verification_success_response
from identity.models.application import NationalIdentificationNumberApplication



class Stripe:
    """
    Stripe class that handle customer creation, payment,
    recurring and canceled recurring payment
    """

    @staticmethod
    def charge_user1(*args,**kwargs):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            amount = 100
            
            metadata = dict(

            )
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency='usd',
                metadata=metadata,
                payment_method_types=['card'],
            )
            
            # Create a transaction record in your database
            transaction = Transaction.objects.create(
                user=kwargs.get("auth_user"),
                amount=amount, 
                stripe_payment_id=intent.id,
                payment_status="PENDING",
                payment_provider="STRIPE"
            )

            response_data = {
                'clientSecret': intent.client_secret,
                "transaction_id": str(transaction.id),
            }
            return success_response(data=response_data)
        except Exception as e:
            logging.error(e)
            logging.error(traceback.print_exc())
            return bad_request_response(message=str(e))
        


    @staticmethod
    def charge_user(request, *args, **kwargs):
        transaction = None
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            amount = 100  
            transaction = Transaction.objects.create(
                user=kwargs.get("auth_user"),
                amount=amount,
                application=kwargs.get("application"),
                payment_status="PENDING",
                payment_provider="STRIPE",
            )


            metadata = {
                "transaction_id": str(transaction.id),
                "application_id": str(transaction.application.id), 
                "user_email": transaction.application.email,
            }
            # Create a Stripe Checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Payment NIN Enrolment',
                        },
                        'unit_amount': int(amount * 100), 
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{request.data.get("redirect_url")}&session_id={{CHECKOUT_SESSION_ID}}&payment_type={transaction.payment_type}',
                cancel_url=f'{request.data.get("redirect_url")}&session_id={{CHECKOUT_SESSION_ID}}&payment_type={transaction.payment_type}',
                metadata=metadata
            )

            transaction.stripe_payment_id = session.id
            transaction.save()

            response_data = {
                'payment_url': session.url,
                "transaction_id": str(transaction.id)
            }
            return success_response(data=response_data)
        except stripe.error.StripeError as e:
            logging.error(e)
            logging.error(traceback.print_exc())
            return bad_request_response(message=str(e))
        except Exception as e:
            logging.error(e)
            logging.error(traceback.print_exc())
            if transaction:transaction.delete()
            return bad_request_response(message=str(e))


    @staticmethod
    def validate_payment(request,redirect_url):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session_id = request.GET.get('session_id')

            if not session_id:return bad_request_response(message="session_id is required on the request header")
            
            session = stripe.checkout.Session.retrieve(session_id)
            
            payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
            
            # Update transaction status in your database
            transaction = Transaction.objects.get(stripe_payment_id=session_id)
            if payment_intent.status == 'succeeded':
                if transaction.payment_status != "SUCCESS":
                    print(payment_intent.metadata)
                    payment_type = transaction.payment_type
                    if payment_type == "NIN":
                        try:
                            application_record = NationalIdentificationNumberApplication.objects.get(id=transaction.application.id)
                            application_record.payment_status = "PAID"
                            application_record.application_status = "SUBMITTED"
                            transaction.payment_status = "SUCCESS"
                            transaction.response = payment_intent
                            transaction.save()

                            
                            # if not application_record.capturing_order_comfirmed:
                            #     success , printscan_response = PrintScan().submit_appointment_order(
                            #     tracking_id_tcn=application_record.capturing_order_ref,
                            #     tracking_id_tcr=application_record.capturing_order_ref,
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
                
            else:
                transaction.payment_status = "FAILED"
                transaction.response = payment_intent
                transaction.save()
                return success_response(message="Payment not successful.")
            
        except Exception as e:
            logging.error(e)
            logging.error(traceback.print_exc())
            return internal_server_error_response(message="Error validating payment.")


    @staticmethod
    def stripe_webhook(request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return bad_request_response()
        except stripe.error.SignatureVerificationError as e:
            logging.error(e)
            logging.error(traceback.print_exc())
            return bad_request_response()

        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            transaction = Transaction.objects.get(stripe_payment_id=payment_intent['id'])
            transaction.status = "SUCCESS"
            transaction.save()

        try:
            url = 'https://eoc3cqj60djento.m.pipedream.net'
            if request.method == 'POST':
                payload = request.body
                webhook_send_request = requests.post(url,data=payload)
                print(webhook_send_request.status_code)
        except Exception as e:
            logging.error(e)
            logging.error(traceback.print_exc())



