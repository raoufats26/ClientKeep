from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Reminder, Client, ActivityLog
from datetime import datetime, date

reminders_bp = Blueprint('reminders', __name__, url_prefix='/reminders')


def log(user_id, action, icon='bell'):
    db.session.add(ActivityLog(
        user_id=user_id, action=action,
        entity='reminder', icon=icon
    ))


@reminders_bp.route('/')
@login_required
def index():
    pending = Reminder.query.filter_by(user_id=current_user.id, is_done=False)\
        .order_by(Reminder.due_date.asc().nullslast()).all()
    done = Reminder.query.filter_by(user_id=current_user.id, is_done=True)\
        .order_by(Reminder.created_at.desc()).limit(10).all()
    clients = Client.query.filter_by(user_id=current_user.id).all()
    return render_template('reminders/index.html',
        pending=pending, done=done,
        clients=clients, today=date.today()
    )


@reminders_bp.route('/add', methods=['POST'])
@login_required
def add():
    title       = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    due_str     = request.form.get('due_date')
    client_id   = request.form.get('client_id') or None

    if not title:
        flash('Reminder title is required.', 'error')
        return redirect(url_for('reminders.index'))

    due_date = None
    if due_str:
        due_date = datetime.strptime(due_str, '%Y-%m-%d').date()

    r = Reminder(
        user_id=current_user.id,
        title=title,
        description=description,
        due_date=due_date,
        client_id=int(client_id) if client_id else None
    )
    db.session.add(r)
    log(current_user.id, f'Reminder "{title}" created', 'bell')
    db.session.commit()
    flash('Reminder added!', 'success')
    return redirect(url_for('reminders.index'))


@reminders_bp.route('/<int:rid>/done', methods=['POST'])
@login_required
def mark_done(rid):
    r = Reminder.query.filter_by(id=rid, user_id=current_user.id).first_or_404()
    r.is_done = True
    log(current_user.id, f'Reminder "{r.title}" completed', 'check-circle')
    db.session.commit()
    flash('Reminder marked as done!', 'success')
    return redirect(url_for('reminders.index'))


@reminders_bp.route('/<int:rid>/delete', methods=['POST'])
@login_required
def delete(rid):
    r = Reminder.query.filter_by(id=rid, user_id=current_user.id).first_or_404()
    db.session.delete(r)
    db.session.commit()
    flash('Reminder deleted.', 'info')
    return redirect(url_for('reminders.index'))
