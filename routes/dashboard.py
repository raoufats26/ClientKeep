from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Client, Invoice, Payment
from extensions import db
from datetime import datetime, date

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Stats
    total_clients = Client.query.filter_by(user_id=current_user.id).count()
    total_invoices = Invoice.query.filter_by(user_id=current_user.id).count()

    pending_invoices = Invoice.query.filter_by(
        user_id=current_user.id, status='pending'
    ).count()

    overdue_invoices = Invoice.query.filter_by(
        user_id=current_user.id, status='overdue'
    ).count()

    # Revenue
    paid_invoices = Invoice.query.filter_by(
        user_id=current_user.id, status='paid'
    ).all()
    total_revenue = sum(inv.amount for inv in paid_invoices)

    # Monthly income (current month)
    now = datetime.utcnow()
    monthly_invoices = Invoice.query.filter(
        Invoice.user_id == current_user.id,
        Invoice.status == 'paid',
        db.extract('month', Invoice.created_at) == now.month,
        db.extract('year', Invoice.created_at) == now.year
    ).all()
    monthly_income = sum(inv.amount for inv in monthly_invoices)

    # Recent clients
    recent_clients = Client.query.filter_by(user_id=current_user.id)\
        .order_by(Client.created_at.desc()).limit(5).all()

    # Recent invoices
    recent_invoices = Invoice.query.filter_by(user_id=current_user.id)\
        .order_by(Invoice.created_at.desc()).limit(5).all()

    return render_template('dashboard/index.html',
        total_clients=total_clients,
        total_invoices=total_invoices,
        pending_invoices=pending_invoices,
        overdue_invoices=overdue_invoices,
        total_revenue=total_revenue,
        monthly_income=monthly_income,
        recent_clients=recent_clients,
        recent_invoices=recent_invoices,
    )
