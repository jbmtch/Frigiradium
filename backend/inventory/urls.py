from django.urls import include, path
from rest_framework import routers

from inventory import views

router = routers.DefaultRouter()
router.register(r"userprofiles", views.UserProfileViewSet)
router.register(r"households", views.HouseholdViewSet)
router.register(r"inventory", views.InventoryViewSet)
router.register(r"userinventory", views.UserInventoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("households/<int:household_id>/inventory/",
         views.InventoryViewSet.as_view({"post": "create"}),
         name="household-inventory-create",
         ),
    path("households/<int:household_id>/inventory/",
         views.InventoryViewSet.as_view({"post": "update"}),
         name="household-inventory-update",
         ),
    path("households/<int:household_id>/inventory/",
         views.InventoryViewSet.as_view({"get": "get_queryset"}),
         name="household-inventory-get",
         ),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]