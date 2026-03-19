from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Client, Invoice, ActivityLog
from extensions import db
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    now = datetime.utcnow()

    total_clients  = Client.query.filter_by(user_id=current_user.id).count()
    total_invoices = Invoice.query.filter_by(user_id=current_user.id).count()

    pending_invoices = Invoice.query.filter_by(user_id=current_user.id, status='pending').count()
    overdue_invoices = Invoice.query.filter_by(user_id=current_user.id, status='overdue').count()

    paid_invoices  = Invoice.query.filter_by(user_id=current_user.id, status='paid').all()
    total_revenue  = sum(i.amount for i in paid_invoices)

    monthly_invoices = Invoice.query.filter(
        Invoice.user_id == current_user.id,
        Invoice.status == 'paid',
        db.extract('month', Invoice.created_at) == now.month,
        db.extract('year',  Invoice.created_at) == now.year
    ).all()
    monthly_income = sum(i.amount for i in monthly_invoices)

    recent_clients  = Client.query.filter_by(user_id=current_user.id).order_by(Client.created_at.desc()).limit(5).all()
    recent_invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.created_at.desc()).limit(5).all()

    # Activity log (latest 8)
    recent_activity = ActivityLog.query.filter_by(user_id=current_user.id)\
        .order_by(ActivityLog.created_at.desc()).limit(8).all()

    # 6-month revenue chart data
    chart_labels = []
    chart_data   = []
    for i in range(5, -1, -1):
        d = now - timedelta(days=i * 30)
        label = d.strftime('%b')
        total = db.session.query(db.func.sum(Invoice.amount)).filter(
            Invoice.user_id == current_user.id,
            Invoice.status  == 'paid',
            db.extract('month', Invoice.created_at) == d.month,
            db.extract('year',  Invoice.created_at) == d.year
        ).scalar() or 0
        chart_labels.append(label)
        chart_data.append(round(total, 2))

    return render_template('dashboard/index.html',
        total_clients=total_clients,
        total_invoices=total_invoices,
        pending_invoices=pending_invoices,
        overdue_invoices=overdue_invoices,
        total_revenue=total_revenue,
        monthly_income=monthly_income,
        recent_clients=recent_clients,
        recent_invoices=recent_invoices,
        recent_activity=recent_activity,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
        now=now,
    )
