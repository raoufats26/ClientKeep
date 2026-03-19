from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Invoice, Client, Payment
from datetime import datetime
import random
import string

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')


def generate_invoice_number():
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    return f'INV-{suffix}'


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
        client_id = request.form.get('client_id')
        service = request.form.get('service', '').strip()
        amount = request.form.get('amount')
        due_date_str = request.form.get('due_date')
        notes = request.form.get('notes', '').strip()

        if not client_id or not service or not amount:
            flash('Client, service, and amount are required.', 'error')
            return render_template('invoices/form.html', clients=clients, action='Add', invoice=None)

        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        invoice = Invoice(
            user_id=current_user.id,
            client_id=int(client_id),
            invoice_number=generate_invoice_number(),
            service=service,
            amount=float(amount),
            due_date=due_date,
            notes=notes,
            status='pending'
        )
        db.session.add(invoice)
        db.session.commit()
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('invoices.index'))

    return render_template('invoices/form.html', clients=clients, action='Add', invoice=None)


@invoices_bp.route('/<int:invoice_id>')
@login_required
def view(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    return render_template('invoices/view.html', invoice=invoice)


@invoices_bp.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    clients = Client.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        invoice.client_id = int(request.form.get('client_id'))
        invoice.service = request.form.get('service', '').strip()
        invoice.amount = float(request.form.get('amount', 0))
        invoice.notes = request.form.get('notes', '').strip()
        due_date_str = request.form.get('due_date')
        if due_date_str:
            invoice.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        db.session.commit()
        flash('Invoice updated!', 'success')
        return redirect(url_for('invoices.view', invoice_id=invoice.id))

    return render_template('invoices/form.html', clients=clients, action='Edit', invoice=invoice)


@invoices_bp.route('/<int:invoice_id>/status/<status>', methods=['POST'])
@login_required
def update_status(invoice_id, status):
    if status not in ['paid', 'pending', 'overdue']:
        flash('Invalid status.', 'error')
        return redirect(url_for('invoices.index'))

    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    invoice.status = status

    if status == 'paid':
        existing = Payment.query.filter_by(invoice_id=invoice.id).first()
        if not existing:
            payment = Payment(invoice_id=invoice.id, amount=invoice.amount)
            db.session.add(payment)

    db.session.commit()
    flash(f'Invoice marked as {status}!', 'success')
    return redirect(url_for('invoices.view', invoice_id=invoice.id))


@invoices_bp.route('/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    db.session.delete(invoice)
    db.session.commit()
    flash('Invoice deleted.', 'info')
    return redirect(url_for('invoices.index'))
