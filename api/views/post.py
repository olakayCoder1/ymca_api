




# posts/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from api.models import Post, UpdateAttachment
from api.serializers.post import AttachmentCreateSerializer, PostCreateUpdateSerializer, PostListSerializer, UpdateAttachmentSerializer
from api.utils.response.response_format import success_response, bad_request_response

import base64, uuid
from django.core.files.base import ContentFile

def base64_to_file(data_url, filename=None):
    try:
        if not data_url.startswith('data:'):
            return None

        format, imgstr = data_url.split(';base64,')  # e.g. data:image/png;base64,...
        ext = format.split('/')[-1]  # 'png', 'jpeg', etc.
        file_name = filename or f"{uuid.uuid4()}.{ext}"
        return ContentFile(base64.b64decode(imgstr), name=file_name)
    except Exception as e:
        return None


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts
    """
    queryset = Post.objects.all().select_related('user').prefetch_related('updateattachment_set')
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['title', 'content']
    # ordering_fields = ['created_at', 'updated_at', 'title']
    serializer_class = PostListSerializer
    ordering = ['-created_at']  


    # def create(self, request, *args, **kwargs):
    #     response = super().create(request, *args, **kwargs)
    #     return success_response(data=response.data, message='Post created successfully', status_code=response.status_code)

    def create(self, request, *args, **kwargs):
        title = request.data.get('title')
        content = request.data.get('content')
        category = request.data.get('category')  # Not in model yet
        posted_by = request.user
        image_base64 = request.data.get('imageBase64')
        attachments = request.data.get('attachments', [])

        # Step 1: Validate required fields
        if not title or not content:
            return Response({"detail": "Title and content are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Process image (optional)
        image_file = None
        if image_base64:
            image_file = base64_to_file(image_base64)
            if not image_file:
                return Response({"detail": "Invalid base64 image format."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Create Post
        post = Post.objects.create(
            title=title,
            content=content,
            user=posted_by,
            category=category,
            image=image_file  # Can be None
        )

        print(post.user)

        # Step 4: Handle attachments (optional)
        for att in attachments:
            base64_data = att.get('base64')
            name = att.get('name') or f"{uuid.uuid4()}"
            if not base64_data:
                continue  # Skip invalid attachment
            file_obj = base64_to_file(base64_data, filename=name)
            if not file_obj:
                continue  # Skip malformed base64
            UpdateAttachment.objects.create(post=post, file=file_obj)



        post = Post.objects.select_related('user').prefetch_related('updateattachment_set').get(id=post.id)


        # Optional: Serialize response (or return data directly)
        return Response(
            # PostListSerializer(post).data,
            status=200
        )
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, message='Post updated successfully', status_code=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return success_response(data=response.data, message='Post partially updated', status_code=response.status_code)
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return success_response(data=response.data, message='Post retrieved successfully', status_code=response.status_code)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message='Post deleted successfully')
    

    def list(self, request, *args, **kwargs):
        # response =  super().list(request, *args, **kwargs)
        query_set = self.get_queryset()
        category = request.GET.get('category')
        if category:
            if category != 'All':
                query_set = query_set.filter(category=category)

        serializer = self.serializer_class(query_set,many=True)

        return success_response(data=serializer.data, message='Posts retrieved successfully')


    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostListSerializer

    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = self.queryset
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            # You might want to add a category field to your Post model
            # For now, we'll skip category filtering
            pass
        
        # Custom search across title and content
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset

    def perform_create(self, serializer):
        """Set the user when creating a post"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Handle post updates"""
        serializer.save()

    def perform_destroy(self, instance):
        """Handle post deletion - clean up files"""
        # Delete associated files
        if instance.image:
            instance.image.delete(save=False)
        
        # Delete attachment files
        for attachment in instance.updateattachment_set.all():
            if attachment.file:
                attachment.file.delete(save=False)
        
        instance.delete()

    @action(detail=True, methods=['get'])
    def attachments(self, request, pk=None):
        """Get attachments for a specific post"""
        post = self.get_object()
        attachments = post.updateattachment_set.all()
        serializer = UpdateAttachmentSerializer(attachments, many=True)
        return success_response(data=serializer.data, message='Attachments retrieved successfully')


    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get post statistics"""
        total_posts = self.get_queryset().count()
        return success_response(data={
            'total_posts': total_posts,
            'user_posts': self.get_queryset().filter(user=request.user).count() if request.user.is_authenticated else 0
        }, message='Post statistics retrieved successfully')



class UpdateAttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attachments
    """
    queryset = UpdateAttachment.objects.all().select_related('post')
    permission_classes = [permissions.IsAuthenticated]


    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create']:
            return AttachmentCreateSerializer
        return UpdateAttachmentSerializer

    def get_queryset(self):
        """Filter attachments based on user permissions"""
        queryset = self.queryset
        
        # Filter by post if provided
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # Users can only see attachments for posts they have access to
        # You might want to implement more specific permission logic here
        return queryset

    def perform_destroy(self, instance):
        """Handle attachment deletion - clean up files"""
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create attachments"""
        attachments_data = request.data.get('attachments', [])
        
        if not attachments_data:
            return bad_request_response(message='No attachments provided')
        
        created_attachments = []
        errors = []
        
        for i, attachment_data in enumerate(attachments_data):
            serializer = AttachmentCreateSerializer(data=attachment_data)
            if serializer.is_valid():
                attachment = serializer.save()
                created_attachments.append(attachment)
            else:
                errors.append({
                    'index': i,
                    'errors': serializer.errors
                })
        
        if errors:
            # If there are errors, you might want to rollback created attachments
            # For now, we'll return partial success
            return success_response(
                data={
                    'created': UpdateAttachmentSerializer(created_attachments, many=True).data,
                    'errors': errors
                },
                message='Some attachments failed to upload',
                status_code=status.HTTP_207_MULTI_STATUS
            )

        
        return success_response(
            data={'created': UpdateAttachmentSerializer(created_attachments, many=True).data},
            message='Attachments created successfully',
            status_code=status.HTTP_201_CREATED
        )
