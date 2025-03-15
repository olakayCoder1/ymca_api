
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

from api.utils.payment.paystack import Paystack
from api.utils.response.response_format import success_response, bad_request_response




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




