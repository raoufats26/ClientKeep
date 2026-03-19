from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Client

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')


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
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        company = request.form.get('company', '').strip()
        notes = request.form.get('notes', '').strip()

        if not name:
            flash('Client name is required.', 'error')
            return render_template('clients/form.html', action='Add')

        client = Client(
            user_id=current_user.id,
            name=name, email=email, phone=phone,
            company=company, notes=notes
        )
        db.session.add(client)
        db.session.commit()
        flash(f'Client "{name}" added successfully!', 'success')
        return redirect(url_for('clients.index'))

    return render_template('clients/form.html', action='Add', client=None)


@clients_bp.route('/<int:client_id>')
@login_required
def view(client_id):
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    return render_template('clients/view.html', client=client)


@clients_bp.route('/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(client_id):
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        client.name = request.form.get('name', '').strip()
        client.email = request.form.get('email', '').strip()
        client.phone = request.form.get('phone', '').strip()
        client.company = request.form.get('company', '').strip()
        client.notes = request.form.get('notes', '').strip()

        if not client.name:
            flash('Client name is required.', 'error')
            return render_template('clients/form.html', action='Edit', client=client)

        db.session.commit()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('clients.view', client_id=client.id))

    return render_template('clients/form.html', action='Edit', client=client)


@clients_bp.route('/<int:client_id>/delete', methods=['POST'])
@login_required
def delete(client_id):
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash(f'Client "{client.name}" deleted.', 'info')
    return redirect(url_for('clients.index'))
