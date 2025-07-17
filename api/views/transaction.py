
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

from account.models import IDCard
from api.serializers.donation import DonationInitiateSerializer
from api.utils.payment.paystack import Paystack
from api.utils.response.response_format import success_response, bad_request_response
import datetime

class StartMembershipDemoView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        id_card, created = IDCard.objects.get_or_create(user=request.user)
        id_card.is_active =True
        id_card.first_time =False
        id_card.expired = False
        # let expired at 30 days from today
        id_card.expired_at = datetime.date.today() + datetime.timedelta(days=30)
        id_card.save()
        return success_response(
            message="Payment successful.",
            data={
                "transaction_id": str('demo-id'),
                "success":True,
                "amount": 10,
                "message": "Payment successful."
            }
        )
                  
        


class InitiateDonationPamentView(generics.GenericAPIView):
    permission_classes = []
    serializer_class  = DonationInitiateSerializer

    def post(self, request, *args, **kwargs):
        
        redirect_url = request.data.get("redirect_url")
        if not redirect_url:
            return bad_request_response(
                message='Redirect URL is required',
            )
        
        return Paystack.charge_user_for_donation(
            request,
            amount=request.data['amount'],
            name=request.data['name'],
            email=request.data['email'],
        )
    

class VerifyDonationPamentView(generics.GenericAPIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        transaction_id = request.data.get("trxn")
        if not transaction_id:
            return bad_request_response(
                message='Transaction ID is required',
            )
        return Paystack.validate_payment_donation(transaction_id)
    
class ActivateMembershipView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        redirect_url = request.data.get("redirect_url")
        if not redirect_url:
            return bad_request_response(
                message='Redirect URL is required',
            )
        
        return Paystack.charge_user(request,request.user.id,transaction_type='ID')


class VerifyPaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        transaction_id = request.data.get("trxn")
        if not transaction_id:
            return bad_request_response(
                message='Transaction ID is required',
            )
        
        return Paystack.validate_payment(transaction_id)




