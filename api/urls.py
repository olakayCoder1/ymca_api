from django.urls import path
from account import views as account_views
from api.views.category import CategoryListView, ChurchListView, YouthGroupListView
from api.views.transaction import ActivateMembershipView, VerifyPaymentView


urlpatterns = [
    path('register/', account_views.RegisterUserView.as_view(), name='register'),
    path('login/', account_views.LoginUserView.as_view(), name='login'),


    path('account/', account_views.ProfileView.as_view(), name='ProfileView'),
    path('account/signature/', account_views.CardSignatureView.as_view(), name='CardSignatureView'),
    path('account/picture/', account_views.ProfileImageView.as_view(), name='ProfileImageView'),
    path('account/change-password/', account_views.PasswordChangeView.as_view(), name='password-change'),
    path('categories', CategoryListView.as_view(), name='CategoryListView'),
    path('churches', ChurchListView.as_view(), name='ChurchListView'),
    path('youth-groups', YouthGroupListView.as_view(), name='YouthGroupListView'),


    path('membership/activation', ActivateMembershipView.as_view(), name='ActivateMembershipView'),
    path('payment/verify', VerifyPaymentView.as_view(), name='VerifyPaymentView'),
]
