from django.urls import path
from account import views as account_views
from api.views.category import CategoryListView, ChurchListView, YouthGroupListView
from api.views.transaction import ActivateMembershipView, InitiateDonationPamentView, VerifyDonationPamentView, StartMembershipDemoView, VerifyPaymentView
from api.views.members import  AdminAddMembersView, AdminGetMemberOverview, AdminMemberRetrieveUpdateDestroyView, AdminMembersBulkUploadView


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

    path('admin/members/', AdminAddMembersView.as_view(), name='YouthGroupListView'),
    path('admin/members/overview', AdminGetMemberOverview.as_view(), name='AdminGetMemberOverview'),
    path('admin/members/upload', AdminMembersBulkUploadView.as_view(), name='AdminMembersBulkUploadView'),
    path('admin/members/<id>', AdminMemberRetrieveUpdateDestroyView.as_view(), name='AdminMemberRetrieveUpdateDestroyView'), 

    path('membership/demo', StartMembershipDemoView.as_view(), name='StartMembershipDemoView'),
    path('membership/activation', ActivateMembershipView.as_view(), name='ActivateMembershipView'),
    path('payment/verify', VerifyPaymentView.as_view(), name='VerifyPaymentView'), 
    path('initiate/donation', InitiateDonationPamentView.as_view(), name='InitiateDonationPamentView'), 
    path('verify/donation', VerifyDonationPamentView.as_view(), name='VerifyDonationPamentView'), 
]
