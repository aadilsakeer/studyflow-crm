from django.conf import settings
from django.core.mail import send_mail


def _send(to_email, subject, body):
    if not to_email:
        return False
    send_mail(
        subject,
        body,
        getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@globvio.com'),
        [to_email],
        fail_silently=True,
    )
    return True


def notify_payment_success(company, amount, invoice_number):
    email = getattr(company.settings, 'billing_email', None) if hasattr(company, 'settings') else None
    email = email or company.email
    return _send(
        email,
        f'Payment received — {invoice_number}',
        f'Your payment of ₹{amount} for {company.name} was successful.\nInvoice: {invoice_number}',
    )


def notify_payment_failed(company, reason=''):
    email = getattr(company.settings, 'billing_email', None) if hasattr(company, 'settings') else None
    email = email or company.email
    return _send(
        email,
        'Payment failed — action required',
        f'Payment for {company.name} failed. {reason}\nUpdate billing at your portal.',
    )


def notify_trial_expiring(company, days_left):
    email = getattr(company.settings, 'billing_email', None) if hasattr(company, 'settings') else None
    email = email or company.email
    return _send(
        email,
        f'Trial expires in {days_left} days',
        f'Your Globvio trial for {company.name} ends in {days_left} days. Upgrade to keep access.',
    )


def notify_renewal_reminder(company, period_end):
    email = getattr(company.settings, 'billing_email', None) if hasattr(company, 'settings') else None
    email = email or company.email
    return _send(
        email,
        'Subscription renewal upcoming',
        f'{company.name} subscription renews on {period_end}. Ensure payment method is valid.',
    )


def notify_ticket_created(ticket):
    email = getattr(ticket.company.settings, 'billing_email', None) if hasattr(ticket.company, 'settings') else None
    email = email or ticket.company.email
    return _send(
        email,
        f'Support ticket #{ticket.id} created',
        f'Subject: {ticket.subject}\nWe will respond shortly.',
    )


def notify_ticket_reply(ticket, message_body):
    email = getattr(ticket.company.settings, 'billing_email', None) if hasattr(ticket.company, 'settings') else None
    email = email or ticket.company.email
    return _send(
        email,
        f'Update on ticket #{ticket.id}',
        f'New reply:\n{message_body[:500]}',
    )
