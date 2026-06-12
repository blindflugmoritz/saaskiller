# === FEATURE: apikeys ===
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ApiKey
from .serializers import ApiKeyCreateSerializer, ApiKeyCreatedSerializer, ApiKeySerializer


class ApiKeyListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all active API keys for the authenticated user."""
        keys = ApiKey.objects.filter(user=request.user, is_active=True)
        serializer = ApiKeySerializer(keys, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new API key. Returns the raw key exactly once."""
        serializer = ApiKeyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        api_key, raw_key = ApiKey.create(
            user=request.user,
            name=serializer.validated_data["name"],
        )

        # Attach raw_key as a transient attribute so the serializer can read it
        api_key.raw_key = raw_key
        out = ApiKeyCreatedSerializer(api_key)
        return Response(out.data, status=status.HTTP_201_CREATED)


class ApiKeyRevokeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        """Revoke (soft-delete) an API key owned by the authenticated user."""
        api_key = get_object_or_404(ApiKey, pk=pk, user=request.user, is_active=True)
        api_key.is_active = False
        api_key.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
# === END FEATURE: apikeys ===
