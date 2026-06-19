from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .health import health_snapshot
from .operations import (
    operations_snapshot,
    validate_razorpay_live,
    validate_stripe_live,
    verify_transactional_email,
)


class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(health_snapshot())


class OperationsDashboardAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(operations_snapshot())

    def post(self, request):
        action = request.data.get('action')
        if action == 'verify_email':
            to = request.data.get('email', request.user.email)
            verify_transactional_email(to)
            return Response({'sent': True, 'to': to})
        if action == 'validate_payments':
            return Response({
                'stripe': validate_stripe_live(),
                'razorpay': validate_razorpay_live(),
            })
        return Response({'error': 'unknown action'}, status=400)


class LaunchChecklistAPIView(APIView):
    from rest_framework.permissions import IsAdminUser

    permission_classes = [IsAdminUser]

    def get(self, request):
        snap = health_snapshot()
        billing = snap['billing']
        items = [
            {'item': 'Database connected', 'done': snap['database']['ok']},
            {'item': 'Required env vars', 'done': snap['environment']['ok']},
            {'item': 'Stripe configured', 'done': billing['stripe_configured']},
            {'item': 'Razorpay configured', 'done': billing['razorpay_configured']},
            {'item': 'Backup directory', 'done': snap['backups']['backup_dir_exists']},
            {'item': 'Sentry (optional)', 'done': bool(__import__('os').getenv('SENTRY_DSN'))},
        ]
        done = sum(1 for i in items if i['done'])
        return Response({
            'items': items,
            'ready_pct': round(done / len(items) * 100),
            'mvp_ready': done >= len(items) - 1,
        })
