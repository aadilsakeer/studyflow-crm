def build_follow_up_message(lead, company_name=''):
    name = lead.first_name.strip()
    org = company_name or 'our team'

    return (
        f'Hi {name}, this is a reminder from {org} '
        f'about your scheduled follow-up. '
        f'Please reply or call us back at your convenience.'
    )


def build_document_reminder_message(student, document):
    name = student.lead.first_name.strip()
    doc_label = document.get_document_type_display()

    return (
        f'Hi {name}, please upload your {doc_label} '
        f'document to continue your application process. '
        f'Reply if you need assistance.'
    )


def build_offer_reminder_message(student, offer):
    name = student.lead.first_name.strip()

    return (
        f'Hi {name}, your offer {offer.offer_number} '
        f'from {offer.university} expires on '
        f'{offer.expiry_date}. Please review it soon.'
    )


def build_visa_update_message(student, visa_case):
    name = student.lead.first_name.strip()
    appointment = visa_case.appointment_date

    if appointment:
        return (
            f'Hi {name}, your visa appointment for '
            f'{visa_case.country} is on {appointment}. '
            f'Please ensure all documents are ready.'
        )

    status_label = visa_case.get_status_display()

    return (
        f'Hi {name}, your visa case for '
        f'{visa_case.country} is now: {status_label}. '
        f'Contact us for any questions.'
    )
