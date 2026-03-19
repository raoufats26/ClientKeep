from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Client, ActivityLog

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')


def log(user_id, action, entity_id=None, icon='users'):
    db.session.add(ActivityLog(
        user_id=user_id, action=action,
        entity='client', entity_id=entity_id, icon=icon
    ))


@clients_bp.route('/')
@login_required
def index():
    clients = Client.query.filter_by(user_id=current_user.id)\
        .order_by(Client.created_at.desc()).all()
    return render_template('clients/index.html', clients=clients)


@clients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        phone   = request.form.get('phone', '').strip()
        company = request.form.get('company', '').strip()
        notes   = request.form.get('notes', '').strip()

        if not name:
            flash('Client name is required.', 'error')
            return render_template('clients/form.html', action='Add', client=None)

        c = Client(user_id=current_user.id, name=name, email=email,
                   phone=phone, company=company, notes=notes)
        db.session.add(c)
        db.session.flush()
        log(current_user.id, f'Client "{name}" added', c.id, 'user-plus')
        db.session.commit()
        flash(f'Client "{name}" added!', 'success')
        return redirect(url_for('clients.index'))

    return render_template('clients/form.html', action='Add', client=None)


@clients_bp.route('/<int:client_id>')
@login_required
def view(client_id):
    c = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    return render_template('clients/view.html', client=c)


@clients_bp.route('/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(client_id):
    c = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        c.name    = request.form.get('name', '').strip()
        c.email   = request.form.get('email', '').strip()
        c.phone   = request.form.get('phone', '').strip()
        c.company = request.form.get('company', '').strip()
        c.notes   = request.form.get('notes', '').strip()

        if not c.name:
            flash('Client name is required.', 'error')
            return render_template('clients/form.html', action='Edit', client=c)

        log(current_user.id, f'Client "{c.name}" updated', c.id, 'pencil')
        db.session.commit()
        flash('Client updated!', 'success')
        return redirect(url_for('clients.view', client_id=c.id))

    return render_template('clients/form.html', action='Edit', client=c)


@clients_bp.route('/<int:client_id>/delete', methods=['POST'])
@login_required
def delete(client_id):
    c = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    name = c.name
    db.session.delete(c)
    log(current_user.id, f'Client "{name}" deleted', icon='trash-2')
    db.session.commit()
    flash(f'Client "{name}" deleted.', 'info')
    return redirect(url_for('clients.index'))
