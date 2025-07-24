import csv
import io
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Count
from django.db.models.functions import TruncMonth
from account.models import Category, Church, IDCard, User, YouthGroup
from account.serializers import RegisterSerializer
from account.serializers import UserSerializer
from api.utils.response.response_format import success_response, paginate_success_response, bad_request_response

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser


class AdminGetMemberOverview(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(is_admin=False)

    def get(self, request):
        overview = request.GET.get('overview')

        # Use one base queryset for all cases
        queryset = User.objects.filter(is_admin=False)
        response = {}

        if overview == 'gender':
            # Get gender breakdown counts
            gender_counts = queryset.values('gender').annotate(count=Count('id'))
            
            # Create a dictionary for easy lookup
            gender_count_dict = {item['gender']: item['count'] for item in gender_counts}
            
            response = [
                {"name": 'Male', 'value': gender_count_dict.get('Male', 0)},
                {"name": 'Female', 'value': gender_count_dict.get('Female', 0)},
                {'name': 'Other', 'value': gender_count_dict.get('Other', 0)}
            ]

        elif overview == 'month':
            from datetime import datetime
            import calendar
            from django.db.models import Q

            # Get current year
            current_year = datetime.now().year
            
            # Get monthly counts for the current year
            monthly_counts = queryset.filter(
                Q(created_at__year=current_year) & 
                Q(created_at__isnull=False)
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                members=Count('id')
            ).order_by('month')
            
            # Convert to dictionary for lookup
            month_data = {
                entry['month'].month: entry['members'] 
                for entry in monthly_counts
            }
            
            # Create a list with all months, using 0 for months with no signups
            response = [
                {
                    'month': calendar.month_abbr[month], 
                    'members': month_data.get(month, 0)
                }
                for month in range(1, 13)
            ]

        else:
            # Default: Total, active, and inactive counts
            total = queryset.count()
            total_active = queryset.filter(is_active=True).count()
            total_inactive = queryset.filter(is_active=False).count()

            response = {
                'total': total,
                'active': total_active,
                'inactive': total_inactive,
                'new': total  # For now, 'new' will return total count as a placeholder
            }

        return success_response(
            data=response
        )

class AdminMembersBulkUploadView(generics.GenericAPIView):
    queryset = User.objects.filter(is_admin=False)
    serializer_class = RegisterSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """
        Handle CSV file upload for bulk member registration
        """
        if 'file' not in request.FILES:
            return bad_request_response(
                message='No file was provided'
            )
            
        file = request.FILES['file']
        
        # Check if file is CSV
        if not file.name.endswith('.csv'):
            return bad_request_response(
                message='Please upload a CSV file'
            )
        
        # Process the CSV file
        try:
            # Decode and process CSV
            csv_data = file.read().decode('utf-8')
            csv_file = io.StringIO(csv_data)
            reader = csv.DictReader(csv_file)
            
            # Track results
            processed_members = []
            errors = []
            first_error = None
            
            # Process all rows within a single transaction
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):  # Start from 2 to account for header row
                    try:
                        # Map CSV fields to expected model fields
                        member_data = {
                            'first_name': row.get('firstName') or row.get('first_name') or '',
                            'last_name': row.get('lastName') or row.get('last_name') or '',
                            'email': row.get('email') or '',
                            'phone_number': row.get('phoneNumber') or row.get('phone_number') or '',
                            'gender': row.get('gender') or 'Other',
                            'unit': row.get('unit') or '',
                            'church': row.get('church') or None,
                            'youth_council_group': row.get('youthCouncilGroup') or row.get('youth_council_group') or None,
                            'category': row.get('category') or 'Adult Member',
                            'id_number': row.get('id_number') or '',
                        }

                        # old_user = User.objects.filter(email=member_data.get('email')).first()

                        # if old_user:
                        #     old_user.delete()
                        #     print(
                        #         f"Deleted {member_data.get('email')}"
                        #     )

                        
                        church = None
                        if member_data.get('church'):
                            church = Church.objects.filter(name=row.get('church')).first()

                        youth_council_group = None
                        if member_data.get('youth_council_group'):
                            youth_council_group = YouthGroup.objects.filter(name=row.get('youth_council_group')).first() 

                        user = User.objects.create(
                            first_name=member_data.get('first_name'),
                            last_name=member_data.get('last_name'),
                            email=member_data.get('email') or '',
                            phone_number=member_data.get('phone_number'),
                            gender=member_data.get('gender'),
                            unit=member_data.get('unit'),
                            church=church,
                            youth_council_group=youth_council_group,
                        )

                        user.set_password('YMCA123456789')
                        user.save()

                        print('First User Created...... : ', user.email)

                        user_card, created = IDCard.objects.get_or_create(user=user)
                        if created and member_data.get('id_number'):
                            user_card.id_number = member_data.get('id_number')
                            user_card.save()

                        # Add successful member to the list
                        processed_members.append(user)

                    except IntegrityError as e:    
                        print(f"Error creating user at row {row_num}")
                        print(e)
                        error_message =  f"Bulk upload failed, error creating user at row {row_num}"
                        raise Exception(error_message)
                    
                    except Exception as e:
                        error_info = {
                            'row': row_num,
                            'data': row,
                            'errors': str(e)
                        }
                        errors.append(error_info)
                        
                        # Store the first error encountered
                        if first_error is None:
                            first_error = error_info
                
                # Check if there were any errors
                if errors and not processed_members:
                    # If all records failed, raise an exception to roll back the entire transaction
                    if first_error:
                        error_message = f"Error at row {first_error['row']}: {first_error['errors']}"
                        raise Exception(error_message)
                    else:
                        raise Exception('All records failed to process')
            
            # Return success response with processed members
            return success_response(
                message=f'Successfully uploaded {len(processed_members)} members' + 
                        (f' with {len(errors)} errors' if errors else ''),
            )
            
        except Exception as e:
            print(e)
            # Transaction will be automatically rolled back if we reach here
            return bad_request_response(
                message=f'Error processing CSV file: {str(e)}'
            )








class AdminAddMembersView(generics.GenericAPIView):
    """
    Your original view for adding individual members
    """
    queryset = User.objects.filter(is_admin=False).order_by('-created_at')
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        data['password'] = 'YMCA123456789'
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data={})

    def get(self, request):
        members = self.get_queryset()
        serializer = UserSerializer(members, many=True, context={'request': request})
        return paginate_success_response(request, serializer.data, int(request.GET.get('page_size', 10)))
    




class AdminMemberRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    queryset = User.objects.filter(is_admin=False).order_by('-created_at')
    serializer_class = UserSerializer
    lookup_field = 'id'



    def delete(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.delete()
            return success_response(
                message="Member deleted successfully"
            )
        except:
            return bad_request_response(
                message='Error deleting user'
            )
        
    def patch(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Member updated successfully"
                )
        except:
            return bad_request_response(
                message='Error updating user'
            )
        


class AdminMemberUpdateDestroyView(generics.GenericAPIView):

    queryset = User.objects.filter(is_admin=False).order_by('-created_at')
    serializer_class = UserSerializer
    lookup_field = 'id'

        
    def put(self, request,id):
        try:
            user = User.objects.get(id=id)
        except:
            return bad_request_response(
                message='User not found'
                )
        try:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Member updated successfully"
                )
        except:
            return bad_request_response(
                message='Error updating user'
            )
        

    
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except:
            return bad_request_response(
                message='User not found'
                )
        try:
            user = self.get_object()
            user.delete()
            return success_response(
                message="Member deleted successfully"
            )
        except:
            return bad_request_response(
                message='Error deleting user'
            )
       
        

