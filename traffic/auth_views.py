from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp.plugins.otp_totp.models import TOTPDevice
import base64

User = get_user_model()

def jwt_for_user(user):
    r = RefreshToken.for_user(user)
    return {"access": str(r.access_token), "refresh": str(r)}

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if not email or not password:
        return JsonResponse({"error": "email and password required"}, status=400)
    if User.objects.filter(username=email).exists():
        return JsonResponse({"error": "user exists"}, status=400)
    u = User.objects.create_user(username=email, email=email, password=password)
    return JsonResponse({"ok": True, "user": u.username})

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    totp_code = request.data.get("totp_code")
    if not email or not password:
        return JsonResponse({"error": "email and password required"}, status=400)
    user = authenticate(username=email, password=password)
    if not user:
        return JsonResponse({"error": "invalid credentials"}, status=401)
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    if device:
        if not totp_code:
            return JsonResponse({"mfa_required": True}, status=401)
        if not device.verify_token(str(totp_code)):
            return JsonResponse({"error": "invalid totp"}, status=401)
    return JsonResponse(jwt_for_user(user))

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_enroll(request):
    user = request.user
    existing = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    if existing:
        return JsonResponse({"enabled": True})
    device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
    if not device:
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=False)
    secret = base64.b32encode(device.bin_key).decode("utf-8").replace("=", "")
    issuer = "TransitApp"
    label = user.username or f"user{user.id}"
    uri = f"otpauth://totp/{issuer}:{label}?secret={secret}&issuer={issuer}"
    return JsonResponse({"secret": secret, "otpauth_uri": uri})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_confirm(request):
    code = request.data.get("totp_code")
    device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
    if not device or not code:
        return JsonResponse({"error": "bad request"}, status=400)
    ok = device.verify_token(str(code))
    if not ok:
        return JsonResponse({"error": "invalid totp"}, status=401)
    device.confirmed = True
    device.save()
    return JsonResponse({"enabled": True})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mfa_disable(request):
    TOTPDevice.objects.filter(user=request.user).delete()
    return JsonResponse({"enabled": False})
