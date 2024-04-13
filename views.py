from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging
from django.core.paginator import Paginator, EmptyPage
from rest_framework.validators import ValidationError
import sys


logger = logging.getLogger('inventory')

class GetProductView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        products = Product.objects.all()
        page_num = int(request.query_params.get('page', 1))
        price_less_than = int(request.query_params.get('price_less_than', sys.maxsize))
        price_greater_than = int(request.query_params.get('price_greater_than', 0))
        order_by = request.query_params.get('order_by')

        if order_by and order_by not in ['name', 'price']:
            logger.error("Unknown order by query params was given")
            return Response("Order by should be either name or price", status=404)
        products = Product.objects.filter(price__gt=price_greater_than, price__lt=price_less_than)

        if order_by:
            products = products.order_by(order_by)
        products_of_the_page = Product.objects.values()
        logger.debug("products for the given query params %s", products)

        paginator = Paginator(products, 2)
        try:
            page_obj = paginator.page(page_num)
        except EmptyPage:
            return Response({"error": "page does not exist"}, status=404)

        return Response({
            "products": products_of_the_page,
            "page": page_num,
            "hasNext": page_obj.has_next(),
            "totalItems": paginator.count,
        })


class POSTProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        logger.debug('Given request data %s',  data)
        name = data.get('name', None)
        description = data.get('description', None)
        price = data.get('price', None)
        stock = data.get('stock', None)
        if not all([name, description, price, stock]):
            logger.warning('Missing some fields in the request')
            return Response('following keys needs to be present: name, description, price, stock', status=400)
        if price < 0:
            return Response("Bad request : Price can't be negative ")
        if stock < 0:
            return Response("Bad Request : Stock can't be negative ")
        
        product = Product.objects.create(name=data['name'],  description=data['description'], price=data['price'], stock=data['stock'])
        logger.debug('product created successfully')
        return Response("Product created successfully", status=201)


class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        logger.debug('Give product_id %s', product_id)
        product = get_object_or_404(Product, id=product_id)
        product_value = self.get_product_values(product)
        logger.debug('the product for the given product id %s is %s', product_id, product_value)
        return Response(product_value)
    
    def put(self, request, product_id):
        logger.debug('Give product_id %s', product_id)
        product = get_object_or_404(Product, id=product_id)
        name = request.data.get('name')
        description = request.data.get('description')
        price = request.data.get('price')
        stock = request.data.get('stock')
        if name or description or price or stock:
            if name is not None:
                product.name = name
            if description is not None:
                product.description = description
            if price is not None:
                product.price = price
            if stock is not None:
                product.stock = stock

            product.save()
            return Response(self.get_product_values(product))
        else:
           raise ValidationError({'detail' : 'Missing required fields'})

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        logger.debug('Product is %s deleted', product_id)
        return Response("Product deleted successfully")
    
    def get_product_values(self, product: Product):
        return {
            "id": str(product.id),
            "name" : product.name, 
            "description": product.description, 
            "price": product.price,
            "stock": product.stock
        }


