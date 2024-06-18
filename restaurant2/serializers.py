from rest_framework import serializers
from .models import Restaurant, Category, Employee, Table, Point, MenuItem, Order, OrderItem, OrderStatusHistory
from users.serializers import UserSerializer

class RestaurantSerializer(serializers.ModelSerializer):
    restaurant = UserSerializer()
    class Meta:
        model = Restaurant
        fields = ["id", "restaurant", "name", "logo", "address", "banner_image", "phone", "description", "time"]

class RestaurantManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "restaurant", "name", "logo", "address", "banner_image", "phone", "description", "time"]

class CategorySerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()
    class Meta:
        model = Category
        fields = ["id", "name", "restaurant"]

class CategoryMangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]

class EmployeeSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    employee = UserSerializer()

    class Meta:
        model = Employee
        fields = ["id", "employee", "name", "phone", "address", "restaurant", "role"]

    def create(self, validated_data):
        employee_data = validated_data.pop('employee')
        user = UserSerializer.objects.create(**employee_data)
        employee = Employee.objects.create(employee=user, **validated_data)
        return employee


# class EmployeeSerializer(serializers.ModelSerializer):
#     restaurant = RestaurantSerializer()
#     employee = UserSerializer()
#     class Meta:
#         model = Employee
#         fields = ["id", "employee", "name", "phone", "address", "restaurant", "role"]
        
class EmployeeManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "employee", "name", "phone", "address", "restaurant", "role"]

class TableSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()
    class Meta:
        model = Table
        fields = ["id", "restaurant", "number", "qr_code"]

class TableManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["number"]

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()
    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ["id", "restaurant", "category", "image", "name", "description", "price"]
        
        
class MenuItemManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "category", "image", "name", "description", "price"]
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "menu_item", "quantity", "employee", "created_at", "updated_at"]
        
class OrderItemManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["menu_item", "quantity", "employee"]

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    user = UserSerializer()
    employee = EmployeeSerializer()
    restaurant = RestaurantSerializer()
    status_history = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()

    def get_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True)
        return serializer.data

    def get_status_history(self, obj):
        status_history = obj.status_history.all()
        return [
            {
                "status": entry.status,
                "timestamp": entry.timestamp,
            }
            for entry in status_history
        ]

    def get_total_cost(self, obj):
        return obj.get_total_cost()

    class Meta:
        model = Order
        fields = ["id", "restaurant", "table", "user", "employee", "timestamp", "status", "paid", "items", "total_cost", "status_history"]


class OrderManageSerializer(serializers.ModelSerializer):
    items = OrderItemManageSerializer(many=True, write_only=True)

    def create(self, validated_data):
        order_items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)
        OrderStatusHistory.objects.create(order=order, status=order.status)
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop("items", None)
        # Update Order
        instance.table = validated_data.get("table", instance.table)
        instance.status = validated_data.get("status", instance.status)
        instance.paid = validated_data.get("paid", instance.paid)
        instance.save()

        if order_items_data is not None:
            # Clear existing order items if any
            OrderItem.objects.filter(order=instance).delete()
            # Add new order items
            for order_item_data in order_items_data:
                OrderItem.objects.create(order=instance, **order_item_data)

        # Record status change
        if 'status' in validated_data:
            OrderStatusHistory.objects.create(order=instance, status=instance.status)

        return instance

    class Meta:
        model = Order
        fields = ["id", "restaurant", "table", "user", "employee", "timestamp", "status", "paid", "items"]

class OrderCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def update(self, instance, validated_data):
        instance.status = "CANCELLED"
        instance.save()
        OrderStatusHistory.objects.create(order=instance, status="CANCELLED")
        return instance


class OrderItemCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id"]

    def update(self, instance, validated_data):
        order = instance.order
        instance.delete()  # Delete the order item

        # Check if the order has any remaining items
        if not order.order_items.exists():
            order.status = "CANCELLED"
            order.save()
            OrderStatusHistory.objects.create(order=order, status="CANCELLED")

        return instance


# It a new Order Item
class OrderItemCreateSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    menu_item = MenuItemSerializer()
    # quantity = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "order", "menu_item", "quantity", "employee", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        instance.order = validated_data.get("order", instance.order)
        instance.menu_item = validated_data.get("menu_item", instance.menu_item)
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.employee = validated_data.get("employee", instance.employee)
        instance.save()
        return instance
    
# Test Order management 2
class OrderItemSerializerList2(serializers.ModelSerializer):
    menu_item = MenuItemSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "employee"]


class OrderItemSerializer2(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "employee"]


class OrderSerializerList2(serializers.ModelSerializer):
    order_items = OrderItemSerializerList2(many=True)
    total_cost = serializers.SerializerMethodField()

    def get_total_cost(self, obj):
        return obj.get_total_cost()

    class Meta:
        model = Order
        fields = [
            "id",
            "restaurant",
            "table",
            "user",
            "employee",
            "status",
            "paid",
            "timestamp",
            "order_items",
            "total_cost",
        ]


class OrderSerializer2(serializers.ModelSerializer):
    order_items = OrderItemSerializer2(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "restaurant",
            "table",
            "user",
            "employee",
            "status",
            "paid",
            "timestamp",
            "order_items",
        ]

    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop("order_items", None)
        instance.restaurant = validated_data.get("restaurant", instance.restaurant)
        instance.table = validated_data.get("table", instance.table)
        instance.user = validated_data.get("user", instance.user)
        instance.employee = validated_data.get("employee", instance.employee)
        instance.status = validated_data.get("status", instance.status)
        instance.paid = validated_data.get("paid", instance.paid)
        instance.save()

        if order_items_data:
            # Update or create order items
            for order_item_data in order_items_data:
                order_item_id = order_item_data.get("id")
                if order_item_id:
                    order_item = OrderItem.objects.get(id=order_item_id, order=instance)
                    order_item.menu_item = order_item_data.get(
                        "menu_item", order_item.menu_item
                    )
                    order_item.quantity = order_item_data.get(
                        "quantity", order_item.quantity
                    )
                    order_item.employee = order_item_data.get(
                        "employee", order_item.employee
                    )
                    order_item.save()
                else:
                    OrderItem.objects.create(order=instance, **order_item_data)

        return instance
