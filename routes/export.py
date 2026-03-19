from flask import Blueprint, make_response
from flask_login import login_required, current_user
from models import Client, Invoice
import csv, io
from datetime import datetime

export_bp = Blueprint('export', __name__, url_prefix='/export')


@export_bp.route('/clients.csv')
@login_required
def clients_csv():
    clients = Client.query.filter_by(user_id=current_user.id)\
        .order_by(Client.created_at.desc()).all()

    si = io.StringIO()
    w  = csv.writer(si)
    w.writerow(['Name', 'Company', 'Email', 'Phone', 'Notes', 'Created'])
    for c in clients:
        w.writerow([c.name, c.company or '', c.email or '',
                    c.phone or '', c.notes or '',
                    c.created_at.strftime('%Y-%m-%d')])

    output   = make_response(si.getvalue())
    filename = f'clients_{datetime.utcnow().strftime("%Y%m%d")}.csv'
    output.headers['Content-Disposition'] = f'attachment; filename={filename}'
    output.headers['Content-Type'] = 'text/csv'
    return output


@export_bp.route('/invoices.csv')
@login_required
def invoices_csv():
    invoices = Invoice.query.filter_by(user_id=current_user.id)\
        .order_by(Invoice.created_at.desc()).all()

    si = io.StringIO()
    w  = csv.writer(si)
    w.writerow(['Invoice #', 'Client', 'Service', 'Amount', 'Status',
                'Due Date', 'Created'])
    for i in invoices:
        w.writerow([
            i.invoice_number, i.client.name, i.service,
            i.amount, i.status,
            i.due_date.strftime('%Y-%m-%d') if i.due_date else '',
            i.created_at.strftime('%Y-%m-%d')
        ])

    output   = make_response(si.getvalue())
    filename = f'invoices_{datetime.utcnow().strftime("%Y%m%d")}.csv'
    output.headers['Content-Disposition'] = f'attachment; filename={filename}'
    output.headers['Content-Type'] = 'text/csv'
    return output
