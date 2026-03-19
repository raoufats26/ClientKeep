from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Invoice, Client, Payment, ActivityLog
from datetime import datetime
import random, string

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')


def gen_invoice_number():
    chars = string.ascii_uppercase + string.digits
    return 'INV-' + ''.join(random.choices(chars, k=6))


def log(user_id, action, entity=None, entity_id=None, icon='file-text'):
    db.session.add(ActivityLog(
        user_id=user_id, action=action,
        entity=entity, entity_id=entity_id, icon=icon
    ))


@invoices_bp.route('/')
@login_required
def index():
    invoices = Invoice.query.filter_by(user_id=current_user.id)\
        .order_by(Invoice.created_at.desc()).all()
    return render_template('invoices/index.html', invoices=invoices)


@invoices_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    clients = Client.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        client_id    = request.form.get('client_id')
        service      = request.form.get('service', '').strip()
        amount       = request.form.get('amount')
        due_date_str = request.form.get('due_date')
        notes        = request.form.get('notes', '').strip()
        is_recurring = request.form.get('is_recurring') == 'on'
        recur_interval = request.form.get('recur_interval', 'monthly')

        if not client_id or not service or not amount:
            flash('Client, service, and amount are required.', 'error')
            return render_template('invoices/form.html', clients=clients, action='Create', invoice=None)

        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        inv = Invoice(
            user_id=current_user.id, client_id=int(client_id),
            invoice_number=gen_invoice_number(),
            service=service, amount=float(amount),
            due_date=due_date, notes=notes, status='pending',
            is_recurring=is_recurring,
            recur_interval=recur_interval if is_recurring else None,
        )
        inv.generate_portal_token()
        db.session.add(inv)
        db.session.flush()

        client = Client.query.get(int(client_id))
        log(current_user.id, f'Invoice {inv.invoice_number} created for {client.name}',
            'invoice', inv.id, 'file-text')
        db.session.commit()
        flash('Invoice created!', 'success')
        return redirect(url_for('invoices.view', invoice_id=inv.id))

    return render_template('invoices/form.html', clients=clients, action='Create', invoice=None)


@invoices_bp.route('/<int:invoice_id>')
@login_required
def view(invoice_id):
    inv = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    return render_template('invoices/view.html', invoice=inv)


@invoices_bp.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(invoice_id):
    inv     = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    clients = Client.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        inv.client_id     = int(request.form.get('client_id'))
        inv.service       = request.form.get('service', '').strip()
        inv.amount        = float(request.form.get('amount', 0))
        inv.notes         = request.form.get('notes', '').strip()
        inv.is_recurring  = request.form.get('is_recurring') == 'on'
        inv.recur_interval= request.form.get('recur_interval', 'monthly') if inv.is_recurring else None
        due_str           = request.form.get('due_date')
        if due_str:
            inv.due_date = datetime.strptime(due_str, '%Y-%m-%d').date()

        log(current_user.id, f'Invoice {inv.invoice_number} updated', 'invoice', inv.id, 'pencil')
        db.session.commit()
        flash('Invoice updated!', 'success')
        return redirect(url_for('invoices.view', invoice_id=inv.id))

    return render_template('invoices/form.html', clients=clients, action='Edit', invoice=inv)


@invoices_bp.route('/<int:invoice_id>/status/<status>', methods=['POST'])
@login_required
def update_status(invoice_id, status):
    if status not in ['paid', 'pending', 'overdue']:
        flash('Invalid status.', 'error')
        return redirect(url_for('invoices.index'))

    inv = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    inv.status = status

    if status == 'paid' and not Payment.query.filter_by(invoice_id=inv.id).first():
        db.session.add(Payment(invoice_id=inv.id, amount=inv.amount))

    icons = {'paid': 'check-circle', 'pending': 'clock', 'overdue': 'alert-triangle'}
    log(current_user.id,
        f'Invoice {inv.invoice_number} marked as {status}',
        'invoice', inv.id, icons[status])
    db.session.commit()
    flash(f'Invoice marked as {status}.', 'success')
    return redirect(url_for('invoices.view', invoice_id=inv.id))


@invoices_bp.route('/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete(invoice_id):
    inv = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    num = inv.invoice_number
    db.session.delete(inv)
    log(current_user.id, f'Invoice {num} deleted', icon='trash-2')
    db.session.commit()
    flash('Invoice deleted.', 'info')
    return redirect(url_for('invoices.index'))


@invoices_bp.route('/<int:invoice_id>/pdf')
@login_required
def download_pdf(invoice_id):
    from flask import make_response
    from weasyprint import HTML
    import io

    inv = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    html_str = render_template('invoices/pdf_template.html', invoice=inv, user=current_user)
    pdf_bytes = HTML(string=html_str).write_pdf()

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={inv.invoice_number}.pdf'
    return response
