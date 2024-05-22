from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ProductSerializer, ProductModel, ProductUpdateSerializer, SaleSerializer, SaleCreateSerializer, SaleModel, SaleDetailModel
from cloudinary.uploader import upload
from django.contrib.auth.models import User
from pprint import pprint
from django.db import transaction

class ProductView(generics.ListAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer

class ProductCreateView(generics.CreateAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    
class ProductUpdateView(generics.UpdateAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductUpdateSerializer
    
class ProductDeleteView(generics.DestroyAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.status = False
            instance.save()
            
            return Response({'message': 'Product deleted!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductUploadImageView(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        try:
            image_file = request.FILES.get('image')
            
            if not image_file:
                return Response({'error': 'No image uploaded!'}, status=status.HTTP_400_BAD_REQUEST)
            
            print(image_file)

            uploaded_image = upload(image_file)
            file_url_name = uploaded_image['secure_url'].split('/')[-1]
            image_path = f'{uploaded_image["resource_type"]}/{uploaded_image["type"]}/V{uploaded_image["version"]}{file_url_name}'
            pprint(uploaded_image)
            
            return Response({'message': 'Image uploaded!', 'image_url': uploaded_image['url'], 'short_url': image_path}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SaleView(generics.ListAPIView):
    queryset = SaleModel.objects.all()
    serializer_class = SaleSerializer
        
class SaleCreateView(generics.CreateAPIView):
    queryset = SaleModel.objects.all()
    serializer_class = SaleCreateSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            
            user = User.objects.get(id=data['user_id'])
            
            sale = SaleModel.objects.create(
                total=data['total'],
                user_id=user,
            )
            sale.save()
            
            for item in data['details']:
                product_id = item['product_id']
                quantity = item['quantity']
                
                product = ProductModel.objects.get(id=product_id)
                if product.stock < quantity:
                    raise Exception(f'Product {product.name} has insufficient stock in the store!')
                
                product.stock -= quantity
                product.save()
                
                sale_detail = SaleDetailModel.objects.create(
                    quantity=quantity,
                    price=item['price'],
                    subtotal=item['subtotal'],
                    product_id=product,
                    sale_id=sale
                )
                
                sale_detail.save()
                
            return Response({'message': 'Sale created!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class SaleUpdateView(generics.UpdateAPIView):
    queryset = SaleModel.objects.all()
    serializer_class = SaleSerializer
    
class SaleDeleteView(generics.DestroyAPIView):
    queryset = SaleModel.objects.all()
    serializer_class = SaleSerializer
    