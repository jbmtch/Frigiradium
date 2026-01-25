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
         views.InventoryViewSet.as_view({"post": "create", "get": "list"}),
         name="household-inventory",
         ),
    path("households/<int:household_id>/inventory/<int:pk>/",
         views.InventoryViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
         name="household-inventory-detail",
         ),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]