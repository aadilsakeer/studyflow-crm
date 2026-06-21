from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Count, Q
from django.utils import timezone

from auditlogs.services import AuditLogService
from core.models import Company

from .models import (
    AssetAssignment,
    Attendance,
    Employee,
    LeaveRequest,
    Payroll,
    Shift,
)

DEFAULT_LEAVE_BALANCE = {
    'annual': 12,
    'sick': 6,
    'used_annual': 0,
    'used_sick': 0,
}


class OwnerHRMService:

    @staticmethod
    def _audit(*, company, user, action, object_id, description):
        if not company or not user:
            return
        AuditLogService.log(
            company=company,
            user=user,
            module='HRM',
            action=action,
            object_id=object_id,
            description=description,
        )

    @staticmethod
    def _employee_brief(emp):
        if not emp:
            return None
        return {
            'id': emp.id,
            'employee_code': emp.employee_code,
            'full_name': emp.full_name,
            'email': emp.email,
            'designation': emp.designation,
            'department': emp.department.name if emp.department else None,
        }

    @classmethod
    def dashboard(cls):
        employees = Employee.objects.filter(is_active=True)
        attendance_today = Attendance.objects.filter(
            attendance_date=timezone.localdate(),
        )
        leaves_pending = LeaveRequest.objects.filter(status='pending')
        payroll_pending = Payroll.objects.filter(payment_status='pending')
        assets_assigned = AssetAssignment.objects.filter(status=AssetAssignment.STATUS_ASSIGNED)
        return {
            'totals': {
                'employees': employees.count(),
                'present_today': attendance_today.filter(status='present').count(),
                'late_today': attendance_today.filter(is_late=True).count(),
                'pending_leaves': leaves_pending.count(),
                'pending_payroll': payroll_pending.count(),
                'assets_assigned': assets_assigned.count(),
            },
            'recent_leaves': cls.list_leaves(status='pending')[:5],
        }

    @classmethod
    def list_employees(cls, *, company_id=None):
        qs = Employee.objects.select_related('department', 'shift').filter(is_active=True)
        if company_id:
            qs = qs.filter(company_id=company_id)
        return [
            {
                **cls._employee_brief(e),
                'company_id': e.company_id,
                'company_name': e.company.name,
                'phone': e.phone,
                'shift': e.shift.name if e.shift else None,
                'leave_balance': e.leave_balance or DEFAULT_LEAVE_BALANCE,
                'joined_at': e.joined_at,
            }
            for e in qs[:500]
        ]

    @classmethod
    def get_employee(cls, employee_id):
        emp = Employee.objects.select_related('department', 'shift', 'company').filter(
            pk=employee_id,
        ).first()
        if not emp:
            return None
        return {
            **cls._employee_brief(emp),
            'company_id': emp.company_id,
            'company_name': emp.company.name,
            'phone': emp.phone,
            'salary_structure': emp.salary_structure,
            'leave_balance': emp.leave_balance or DEFAULT_LEAVE_BALANCE,
            'shift_id': emp.shift_id,
            'timeline': cls._employee_timeline(emp),
        }

    @classmethod
    def _employee_timeline(cls, emp):
        events = []
        for a in AssetAssignment.objects.filter(employee=emp).order_by('-assigned_at')[:20]:
            events.append({
                'type': 'asset',
                'title': f'{a.asset_type}: {a.asset_name}',
                'body': a.status,
                'created_at': a.assigned_at,
            })
        for lv in LeaveRequest.objects.filter(employee_profile=emp).order_by('-applied_at')[:20]:
            events.append({
                'type': 'leave',
                'title': f'Leave {lv.status}',
                'body': lv.reason,
                'created_at': lv.applied_at,
            })
        events.sort(key=lambda e: e['created_at'], reverse=True)
        return events[:30]

    @classmethod
    def create_employee(cls, *, actor, data):
        company = Company.objects.filter(pk=data['company_id']).first()
        if not company:
            return None
        emp = Employee.objects.create(
            company=company,
            user_id=data.get('user_id'),
            employee_code=data['employee_code'],
            full_name=data['full_name'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            designation=data.get('designation', ''),
            department_id=data.get('department_id'),
            shift_id=data.get('shift_id'),
            salary_structure=data.get('salary_structure', {}),
            leave_balance=data.get('leave_balance', DEFAULT_LEAVE_BALANCE.copy()),
            joined_at=data.get('joined_at'),
        )
        cls._audit(
            company=company, user=actor, action='create_employee',
            object_id=emp.id, description=f'Created employee {emp.full_name}',
        )
        return cls.get_employee(emp.id)

    @classmethod
    def check_in(cls, *, actor, employee_id, latitude=None, longitude=None):
        emp = Employee.objects.select_related('shift', 'company').filter(pk=employee_id).first()
        if not emp or not emp.user:
            return None
        today = timezone.localdate()
        now = timezone.now()
        att, _ = Attendance.objects.get_or_create(
            company=emp.company,
            employee=emp.user,
            attendance_date=today,
            defaults={'status': 'present', 'employee_profile': emp},
        )
        att.check_in_at = now
        att.check_in = now.time()
        att.check_in_latitude = latitude
        att.check_in_longitude = longitude
        att.employee_profile = emp
        att.shift = emp.shift
        att.is_late = cls._is_late(now.time(), emp.shift)
        att.save()
        cls._audit(
            company=emp.company, user=actor, action='check_in',
            object_id=att.id, description=f'Check-in {emp.full_name}',
        )
        return cls._serialize_attendance(att)

    @classmethod
    def check_out(cls, *, actor, employee_id, latitude=None, longitude=None):
        emp = Employee.objects.select_related('company', 'user').filter(pk=employee_id).first()
        if not emp or not emp.user:
            return None
        today = timezone.localdate()
        now = timezone.now()
        att = Attendance.objects.filter(
            company=emp.company, employee=emp.user, attendance_date=today,
        ).first()
        if not att:
            return None
        att.check_out_at = now
        att.check_out = now.time()
        att.check_out_latitude = latitude
        att.check_out_longitude = longitude
        att.save()
        cls._audit(
            company=emp.company, user=actor, action='check_out',
            object_id=att.id, description=f'Check-out {emp.full_name}',
        )
        return cls._serialize_attendance(att)

    @staticmethod
    def _is_late(check_time, shift):
        if not shift:
            return False
        grace = timedelta(minutes=shift.grace_minutes)
        start = datetime.combine(datetime.today(), shift.start_time)
        allowed = (start + grace).time()
        return check_time > allowed

    @classmethod
    def _serialize_attendance(cls, att):
        return {
            'id': att.id,
            'employee': att.employee_profile_id and cls._employee_brief(att.employee_profile),
            'attendance_date': att.attendance_date,
            'status': att.status,
            'check_in_at': att.check_in_at,
            'check_out_at': att.check_out_at,
            'check_in_latitude': att.check_in_latitude,
            'check_in_longitude': att.check_in_longitude,
            'check_out_latitude': att.check_out_latitude,
            'check_out_longitude': att.check_out_longitude,
            'is_late': att.is_late,
        }

    @classmethod
    def list_attendance(cls, *, date=None):
        qs = Attendance.objects.select_related('employee_profile').order_by('-attendance_date')
        if date:
            qs = qs.filter(attendance_date=date)
        return [cls._serialize_attendance(a) for a in qs[:200]]

    @classmethod
    def apply_leave(cls, *, actor, data):
        emp = Employee.objects.select_related('user', 'company').filter(
            pk=data['employee_id'],
        ).first()
        if not emp or not emp.user:
            return None
        leave = LeaveRequest.objects.create(
            employee=emp.user,
            employee_profile=emp,
            start_date=data['start_date'],
            end_date=data['end_date'],
            reason=data.get('reason', ''),
            leave_type=data.get('leave_type', 'annual'),
        )
        cls._audit(
            company=emp.company, user=actor, action='apply_leave',
            object_id=leave.id, description=f'Leave applied for {emp.full_name}',
        )
        return cls._serialize_leave(leave)

    @classmethod
    def review_leave(cls, *, actor, leave_id, status, notes=''):
        leave = LeaveRequest.objects.select_related(
            'employee_profile', 'employee_profile__company', 'employee',
        ).filter(pk=leave_id).first()
        if not leave:
            return None
        leave.status = status
        leave.approved_by = actor
        leave.reviewer_notes = notes
        leave.save()
        if status == 'approved' and leave.employee_profile:
            cls._deduct_leave_balance(leave)
        company = leave.employee_profile.company if leave.employee_profile else leave.employee.company
        cls._audit(
            company=company, user=actor, action=f'leave_{status}',
            object_id=leave.id, description=f'Leave {status} for {leave.employee.username}',
        )
        return cls._serialize_leave(leave)

    @classmethod
    def _deduct_leave_balance(cls, leave):
        emp = leave.employee_profile
        balance = dict(emp.leave_balance or DEFAULT_LEAVE_BALANCE)
        days = (leave.end_date - leave.start_date).days + 1
        key = f'used_{leave.leave_type}' if leave.leave_type in ('annual', 'sick') else 'used_annual'
        balance[key] = balance.get(key, 0) + days
        emp.leave_balance = balance
        emp.save(update_fields=['leave_balance'])

    @classmethod
    def _serialize_leave(cls, leave):
        emp = leave.employee_profile
        return {
            'id': leave.id,
            'employee': cls._employee_brief(emp) if emp else {'name': leave.employee.username},
            'start_date': leave.start_date,
            'end_date': leave.end_date,
            'leave_type': leave.leave_type,
            'reason': leave.reason,
            'status': leave.status,
            'reviewer_notes': leave.reviewer_notes,
            'applied_at': leave.applied_at,
        }

    @classmethod
    def list_leaves(cls, *, status=None):
        qs = LeaveRequest.objects.select_related('employee_profile').order_by('-applied_at')
        if status:
            qs = qs.filter(status=status)
        return [cls._serialize_leave(l) for l in qs[:200]]

    @classmethod
    def create_payroll(cls, *, actor, data):
        emp = Employee.objects.select_related('company', 'user').filter(
            pk=data['employee_id'],
        ).first()
        if not emp or not emp.user:
            return None
        structure = data.get('salary_structure') or emp.salary_structure or {}
        basic = Decimal(str(structure.get('basic', data.get('basic_salary', 0))))
        deductions = Decimal(str(data.get('deductions', 0)))
        net = basic - deductions
        payroll = Payroll.objects.create(
            company=emp.company,
            employee=emp.user,
            employee_profile=emp,
            month=data['month'],
            year=data['year'],
            basic_salary=basic,
            deductions=deductions,
            net_salary=net,
            salary_structure=structure,
            payslip={
                'employee': emp.full_name,
                'month': data['month'],
                'year': data['year'],
                'basic': str(basic),
                'deductions': str(deductions),
                'net': str(net),
            },
            payment_status='pending',
        )
        cls._audit(
            company=emp.company, user=actor, action='create_payroll',
            object_id=payroll.id, description=f'Payroll for {emp.full_name}',
        )
        return cls._serialize_payroll(payroll)

    @classmethod
    def update_payroll_status(cls, *, actor, payroll_id, payment_status):
        payroll = Payroll.objects.select_related('company', 'employee_profile').filter(
            pk=payroll_id,
        ).first()
        if not payroll:
            return None
        payroll.payment_status = payment_status
        payroll.status = 'paid' if payment_status == 'paid' else payroll.status
        if payment_status == 'paid':
            payroll.paid_at = timezone.now()
        payroll.save()
        cls._audit(
            company=payroll.company, user=actor, action='update_payroll_status',
            object_id=payroll.id, description=f'Payroll status → {payment_status}',
        )
        return cls._serialize_payroll(payroll)

    @classmethod
    def _serialize_payroll(cls, p):
        return {
            'id': p.id,
            'employee': cls._employee_brief(p.employee_profile),
            'month': p.month,
            'year': p.year,
            'basic_salary': p.basic_salary,
            'deductions': p.deductions,
            'net_salary': p.net_salary,
            'salary_structure': p.salary_structure,
            'payslip': p.payslip,
            'payment_status': p.payment_status,
            'paid_at': p.paid_at,
        }

    @classmethod
    def list_payroll(cls):
        qs = Payroll.objects.select_related('employee_profile').order_by('-year', '-month')
        return [cls._serialize_payroll(p) for p in qs[:200]]

    @classmethod
    def assign_asset(cls, *, actor, data):
        emp = Employee.objects.select_related('company').filter(pk=data['employee_id']).first()
        if not emp:
            return None
        asset = AssetAssignment.objects.create(
            company=emp.company,
            employee=emp,
            asset_type=data['asset_type'],
            asset_name=data['asset_name'],
            serial_number=data.get('serial_number', ''),
            notes=data.get('notes', ''),
        )
        cls._audit(
            company=emp.company, user=actor, action='assign_asset',
            object_id=asset.id, description=f'Assigned {asset.asset_name} to {emp.full_name}',
        )
        return cls._serialize_asset(asset)

    @classmethod
    def return_asset(cls, *, actor, asset_id):
        asset = AssetAssignment.objects.select_related('employee', 'company').filter(
            pk=asset_id, status=AssetAssignment.STATUS_ASSIGNED,
        ).first()
        if not asset:
            return None
        asset.status = AssetAssignment.STATUS_RETURNED
        asset.returned_at = timezone.now()
        asset.save()
        cls._audit(
            company=asset.company, user=actor, action='return_asset',
            object_id=asset.id, description=f'Returned {asset.asset_name}',
        )
        return cls._serialize_asset(asset)

    @classmethod
    def _serialize_asset(cls, a):
        return {
            'id': a.id,
            'employee': cls._employee_brief(a.employee),
            'asset_type': a.asset_type,
            'asset_name': a.asset_name,
            'serial_number': a.serial_number,
            'status': a.status,
            'assigned_at': a.assigned_at,
            'returned_at': a.returned_at,
            'notes': a.notes,
        }

    @classmethod
    def list_assets(cls, *, employee_id=None, serial_number=None):
        qs = AssetAssignment.objects.select_related('employee').order_by('-assigned_at')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if serial_number:
            qs = qs.filter(serial_number=serial_number)
        return [cls._serialize_asset(a) for a in qs[:200]]

    @classmethod
    def asset_history(cls, *, serial_number):
        return cls.list_assets(serial_number=serial_number)
