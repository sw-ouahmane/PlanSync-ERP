import os
from flask import current_app
from flask_login import current_user
import calendar
from collections import defaultdict
from flask import request
from flask_login import login_required, current_user
from flask import render_template, url_for, request, redirect, flash, send_file
from app.models import db, User, Todo
from flask_login import current_user, login_required
from datetime import datetime
from flask import Blueprint
import io
from weasyprint import HTML


bp = Blueprint('tasks', __name__)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    # Use current_user instead of querying User from session
    user = current_user

    # Check if the task is validated and validated by another admin
    if task_to_delete.status == 'Validated' and task_to_delete.validated_by != user.username:
        return 'You cannot delete a validated task validated by another admin.'

    # Ensure the current user owns the task or is allowed to delete it
    if task_to_delete.user_id != user.id:
        return 'You are not authorized to delete this task.'

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('main.task_master'))
    except Exception as e:
        return f'There was a problem deleting that task: {e}'


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    task = Todo.query.get_or_404(id)

    # Check if the task is validated and if another admin validated it
    if task.status == 'Validated' and task.validated_by != current_user.username:
        return 'You cannot update a validated task validated by another admin.'

    # Ensure the current user owns the task or is allowed to update it
    if task.user_id != current_user.id:
        return 'You are not authorized to update this task.'

    if request.method == 'POST':
        task.date = request.form['date']
        task.shift = request.form['shift']
        task.poste = request.form['poste']
        task.grue = request.form['grue']  # Match the HTML field name
        task.navire = request.form['navire']
        task.marchandise = request.form['marchandise']
        task.nb_cs_pcs = request.form['nb_cs_pcs']
        task.unite = request.form['unite']
        task.raclage = request.form['raclage']
        task.comentaire = request.form['comentaire']

        try:
            db.session.commit()
            return redirect(url_for('main.task_master'))  # Redirect to 'index'
        except Exception as e:
            return f'There was an issue updating your task: {e}'

    return render_template('update.html', task=task)


@bp.route('/add_affectation', methods=['GET', 'POST'])
@login_required
def add_affectation():
    if request.method == 'POST':
        try:
            # Retrieve form data
            date_str = request.form.get('date')
            shift = request.form.get('shift')
            poste = request.form.get('poste')
            grue = request.form.get('grue')
            navire = request.form.get('navire')
            marchandise = request.form.get('marchandise')
            nb_cs_pcs = request.form.get('nb_cs_pcs')
            unite = request.form.get('unite')
            raclage = request.form.get('raclage')
            comentaire = request.form.get('comentaire')

            # Ensure 'current_user' is used
            user_id = current_user.id

            # Convert date string to datetime object
            date_created = datetime.strptime(
                date_str, '%Y-%m-%d')  # Corrected format

            # Create a new Todo object
            new_task = Todo(
                content=None,  # Adjust this as needed
                shift=shift,
                poste=poste,
                grue=grue,
                navire=navire,
                marchandise=marchandise,
                nb_cs_pcs=nb_cs_pcs,
                unite=unite,
                raclage=raclage,
                comentaire=comentaire,
                date_created=date_created,
                user_id=user_id
            )

            # Add to the database
            db.session.add(new_task)
            db.session.commit()

            return redirect(url_for('main.task_master'))

        except Exception as e:
            # Print the error for debugging
            print(f"An error occurred: {e}")
            return "There was a problem adding the affectation."

    return render_template('add_affectation.html')


@bp.route('/view_user_tasks/<int:user_id>', methods=['GET', 'POST'])
@login_required
def view_user_tasks(user_id):
    user = User.query.get_or_404(user_id)

    # Get the current page number from the query string or default to 1
    page = request.args.get('page', 1, type=int)

    # Retrieve search parameters (year and month) from query string
    search_year = request.args.get('year', type=int)
    search_month = request.args.get('month', type=int)

    # Start building the query for tasks
    query = Todo.query.filter_by(user_id=user_id)

    # Apply search filters if year and month are provided
    if search_year and search_month:
        query = query.filter(db.extract('year', Todo.date_created) == search_year,
                             db.extract('month', Todo.date_created) == search_month)

    # Paginate the tasks
    tasks = query.paginate(page=page, per_page=10)

    # Handle POST request (validation/rejection of tasks)
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        action = request.form.get('action')
        remark = request.form.get('remark')

        task = Todo.query.get(task_id)
        if not task:
            flash('Task not found.', 'danger')
            return redirect(url_for('tasks.view_user_tasks', user_id=user_id, page=page))

        # Check task status and apply actions
        if task.status == 'Rejected' and task.validated_by != current_user.username:
            flash(
                'This task has already been rejected by another admin. You cannot modify it.', 'danger')
        else:
            if action == 'validate':
                task.status = 'Validated'
                task.validated_by = current_user.username
                task.remark = remark
                flash('Task validated successfully.', 'success')
            elif action == 'reject':
                task.status = 'Rejected'
                task.validated_by = current_user.username
                task.remark = remark
                flash('Task rejected successfully.', 'success')
            else:
                flash('Invalid action.', 'danger')

        # Commit changes to the database
        db.session.commit()

        # Redirect to the same page to reflect the changes, keeping the pagination
        return redirect(url_for('tasks.view_user_tasks', user_id=user_id, page=page))

    # Render the template with the user, paginated tasks, and search values
    return render_template('view_tasks.html', user=user, tasks=tasks, search_year=search_year, search_month=search_month)


@bp.route('/validate_task/<int:task_id>/<string:action>', methods=['POST'])
@login_required
def validate_task(task_id, action):
    # Ensure only admins can validate or reject tasks
    if not current_user.is_admin:
        return redirect(url_for('tasks.view_user_tasks', user_id=current_user.id))

    task = Todo.query.get_or_404(task_id)
    # Get the Escale input from the form
    escale = request.form.get('Escale', '')
    remark = request.form.get('remark', '')

    # Update the task with the Escale value
    if escale:
        task.Escale = escale

    # Identify the initial admin created at app startup
    initial_admin_matricule = 'ADMIN0001'

    # If the task was processed by another admin, no further action is allowed unless it's the initial admin
    if task.is_validated and task.validated_by != current_user.username and current_user.matricule != initial_admin_matricule:
        return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

    if task.status == 'Rejected' and task.validated_by != current_user.username and current_user.matricule != initial_admin_matricule:
        return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

    # Handle task validation
    if action == 'validate':
        if task.is_validated and task.validated_by == current_user.username:
            pass  # No further action needed
        elif task.status == 'Rejected' and (task.validated_by == current_user.username or current_user.matricule == initial_admin_matricule):
            # Allow the same admin who rejected the task or the initial admin to reverse their decision
            task.status = 'Validated'
            task.is_validated = True
            task.remark = remark
            task.validated_by = current_user.username
        elif task.is_validated or task.status == 'Rejected':
            pass  # No action allowed if processed by another admin
        else:
            task.status = 'Validated'
            task.is_validated = True
            task.validated_by = current_user.username  # Store current admin's username
            task.remark = remark

    # Handle task rejection
    elif action == 'reject':
        if task.status == 'Rejected' and task.validated_by == current_user.username:
            pass  # No further action needed
        elif task.is_validated and (task.validated_by == current_user.username or current_user.matricule == initial_admin_matricule):
            # Allow the same admin who validated the task or the initial admin to reverse their decision
            task.status = 'Rejected'
            task.is_validated = False  # Set to False if rejected
            task.remark = remark
            task.validated_by = current_user.username
        elif task.is_validated or task.status == 'Rejected':
            pass  # No action allowed if processed by another admin
        else:
            task.status = 'Rejected'
            task.is_validated = False  # Set to False if rejected
            task.validated_by = current_user.username  # Store current admin's username
            task.remark = remark

    else:
        return "Invalid action", 400

    db.session.commit()
    return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))


@bp.route('/add_escale/<int:task_id>', methods=['POST'])
def add_escale(task_id):
    task = Todo.query.get_or_404(task_id)

    # Check if the user is an admin using the `is_admin` attribute
    if not current_user.is_admin:
        flash("You do not have permission to add an Escale.", "danger")
        return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

    # Process form data
    escale = request.form.get('Escale')
    if escale:
        task.Escale = escale
        db.session.commit()
        flash('Escale added successfully!', 'success')
    else:
        flash('Please enter a valid Escale.', 'danger')

    return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))


@bp.route('/statistiques')
@login_required  # Ensure the user is logged in
def statistiques():
    # Get the selected filters from the form
    month_filter = request.args.get('month')
    year_filter = request.args.get('year')
    escale_filter = request.args.get('Escale')
    marchandise_filter = request.args.get('marchandise')
    grue_filter = request.args.get('grue')

    # Query validated tasks for the current user
    query = Todo.query.filter_by(status='Validated', user_id=current_user.id)

    # Apply filters if selected
    if month_filter:
        query = query.filter(db.extract(
            'month', Todo.date_created) == month_filter)
    if year_filter:
        query = query.filter(db.extract(
            'year', Todo.date_created) == year_filter)
    if escale_filter:
        query = query.filter_by(Escale=escale_filter)
    if marchandise_filter:
        query = query.filter_by(marchandise=marchandise_filter)
    if grue_filter:
        query = query.filter_by(grue=grue_filter)

    # Get all validated tasks based on filters
    validated_todos = query.all()

    # Dictionary to store count of validated tasks by month
    tasks_per_month = defaultdict(int)

    # Populate tasks_per_month with filtered data
    for todo in validated_todos:
        if todo.date_created:
            month = todo.date_created.month
            tasks_per_month[month] += 1

    # Sort and prepare data for display
    months = [calendar.month_name[i] for i in sorted(tasks_per_month)]
    task_counts = [tasks_per_month[i] for i in sorted(tasks_per_month)]

    # Fetch available years for year dropdown
    available_years = sorted(set(
        todo.date_created.year for todo in Todo.query.filter_by(user_id=current_user.id)))

    # Fetch distinct values for the filters
    available_escales = sorted(set(todo.Escale for todo in Todo.query.filter_by(
        user_id=current_user.id) if todo.Escale))
    available_marchandises = sorted(set(todo.marchandise for todo in Todo.query.filter_by(
        user_id=current_user.id) if todo.marchandise))
    available_grues = sorted(set(todo.grue for todo in Todo.query.filter_by(
        user_id=current_user.id) if todo.grue))

    # Pass month names and other data to the template
    return render_template('statistiques.html',
                           months=months,
                           task_counts=task_counts,
                           available_years=available_years,
                           available_escales=available_escales,
                           available_marchandises=available_marchandises,
                           available_grues=available_grues,
                           month_names=calendar.month_name,
                           stats=zip(months, task_counts))


@bp.route('/export', methods=['GET'])
def export():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not month:
        return redirect(url_for('tasks.task_master'))

    # Fetch tasks for the selected year and month
    tasks = Todo.query.filter(
        db.extract('year', Todo.date_created) == year,
        db.extract('month', Todo.date_created) == month
    ).all()

    # Render the report template (without the excluded fields)
    html = render_template('export_template.html', tasks=tasks)

    # Convert the HTML to PDF
    pdf = HTML(string=html, base_url=request.url_root).write_pdf()

    # Return the PDF as a downloadable file
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Task_Report_Month_{month}.pdf'
    )


@bp.route('/get_logo_path', methods=['GET'])
def get_logo_path():
    # Get the absolute path for the logo image
    logo_path = os.path.abspath(os.path.join(
        current_app.root_path, 'static/images/logoMM.PNG'))
    return f'The absolute path for the logo is: {logo_path}'
