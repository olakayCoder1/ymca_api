from django.urls import path
from account import views as account_views
from api.views.category import CategoryListView, ChurchListView, YouthGroupListView
from api.views.transaction import ActivateMembershipView, InitiateDonationPamentView, TotalMembersCountView, VerifyDonationPamentView, StartMembershipDemoView, VerifyPaymentView
from api.views.members import  AdminAddMembersView,AdminGetSingleRequestView, AdminGetMemberOverview, AdminMemberRetrieveUpdateDestroyView, AdminMemberUpdateDestroyView, AdminMembersBulkUploadView, AdminUpdateRequestStatusView, AdminUserRequestListView, CreateUserRequestView, UserRequestDetailView, UserRequestListView, VerifyCardIdNumberView


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import post as post_view
from api.views.staff import PrincipalOfficersListView, ManagementStaffListView

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'posts', post_view.PostViewSet, basename='posts')
router.register(r'attachments', post_view.UpdateAttachmentViewSet, basename='attachments')



urlpatterns = [

    path('', include(router.urls)),
    # path('posts/bulk-attachments/', post_view.BulkAttachmentUploadView.as_view(), name='bulk-attachments'),

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
    path('admin/members/<id>/update', AdminMemberUpdateDestroyView.as_view(), name='AdminMemberUpdateDestroyView'), 
        # User endpoints
    path('requests/', CreateUserRequestView.as_view(), name='create-request'),
    path('requests/list/', UserRequestListView.as_view(), name='list-requests'),
    path('requests/<uuid:pk>/', UserRequestDetailView.as_view(), name='request-detail'),
    
    # Admin endpoints
    path('admin/requests/', AdminUserRequestListView.as_view(), name='admin-list-requests'),
    path('admin/requests/<uuid:pk>/', AdminGetSingleRequestView.as_view(), name='admin-get-single-request'),
    path('admin/requests/<uuid:pk>/status/', AdminUpdateRequestStatusView.as_view(), name='admin-update-request-status'),

    path('id-verification/<id_number>', VerifyCardIdNumberView.as_view(), name='VerifyCardIdNumberView'),

    path('membership/demo', StartMembershipDemoView.as_view(), name='StartMembershipDemoView'),
    path('membership/activation', ActivateMembershipView.as_view(), name='ActivateMembershipView'),
    path('payment/verify', VerifyPaymentView.as_view(), name='VerifyPaymentView'), 
    path('initiate/donation', InitiateDonationPamentView.as_view(), name='InitiateDonationPamentView'), 
    path('verify/donation', VerifyDonationPamentView.as_view(), name='VerifyDonationPamentView'), 

    path('total-members-count', TotalMembersCountView.as_view(), name='TotalMembersCountView'), 
    
    # Subscription endpoints
    path('subscriptions/', include('subscription.urls')),

    # Staff endpoints
    path('staff/principal-officers/', PrincipalOfficersListView.as_view(), name='PrincipalOfficersListView'),
    path('staff/management-staff/', ManagementStaffListView.as_view(), name='ManagementStaffListView'),
]
