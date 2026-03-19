from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import Invoice
from extensions import db

portal_bp = Blueprint('portal', __name__, url_prefix='/portal')


@portal_bp.route('/<token>')
def view(token):
    inv = Invoice.query.filter_by(portal_token=token).first_or_404()
    return render_template('portal/view.html', invoice=inv)


@portal_bp.route('/<token>/confirm-paid', methods=['POST'])
def confirm_paid(token):
    inv = Invoice.query.filter_by(portal_token=token).first_or_404()
    if inv.status == 'pending':
        inv.status = 'paid'
        from models import Payment
        db.session.add(Payment(invoice_id=inv.id, amount=inv.amount))
        db.session.commit()
        flash('Payment confirmed. Thank you!', 'success')
    return redirect(url_for('portal.view', token=token))
