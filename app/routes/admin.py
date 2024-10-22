from flask_login import login_required
from app.utils import get_active_sessions_count
from app.models import db, User, Todo
from app.models import Conference
from flask import render_template, url_for, request, redirect, session, flash,  url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import calendar
import json
from datetime import datetime
from flask import Blueprint
from flask_login import login_required, current_user
from flask import send_file
from collections import defaultdict


bp = Blueprint('admin', __name__)


@bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    # Fetch user statistics
    total_users = User.query.count()  # Get total number of users
    pending_users = User.query.filter_by(
        is_admin=False, is_approved=False).all()
    normal_users = User.query.filter_by(is_admin=False, is_approved=True).all()
    admins = User.query.filter_by(is_admin=True).all()

    active_sessions = get_active_sessions_count()  # Get active sessions count

    # Get search parameter
    prenom = request.args.get('prenom', '')
    conferences = Conference.query.all()
    print(f"Conferences fetched: {conferences}")  # Debugging line

    # Get current page and set tasks per page
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Start with the base query
    query = Todo.query.join(User).filter(Todo.user_id == User.id)

    # Filter by prenom (from User model)
    if prenom:
        query = query.filter(User.prenom.ilike(f'%{prenom}%'))

    # Paginate the query
    tasks = query.paginate(page=page, per_page=per_page)

    return render_template('admin/admin.html',
                           total_users=total_users,
                           pending_users=pending_users,
                           normal_users=normal_users,
                           admins=admins,
                           conferences=conferences,
                           active_sessions=active_sessions,
                           tasks=tasks)


@bp.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    # Ensure that only admins can delete users
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    user_to_delete = User.query.get_or_404(id)

    try:
        # Option 1: Delete all tasks associated with the user
        Todo.query.filter_by(user_id=id).delete()

        # Option 2: Reassign tasks to another user or set to null if allowed
        # Todo.query.filter_by(user_id=id).update({Todo.user_id: None})

        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    except Exception as e:
        return f'There was a problem deleting the user: {e}'


@bp.route('/delete_admin/<int:id>')
@login_required
def delete_admin(id):
    # Check if the current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    # Fetch the admin to be deleted
    admin_user = User.query.get_or_404(id)

    # Check if the user to be deleted is an admin
    if not admin_user.is_admin:
        return 'The user is not an admin.'

    # Prevent deletion of the super admin
    if admin_user.is_super_admin:
        return 'You cannot delete the super admin.'

    # Proceed with deletion
    try:
        db.session.delete(admin_user)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    except Exception as e:
        return f'There was a problem deleting the admin user: {e}'


@bp.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    # Check if the current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Verify the current password
        if not check_password_hash(current_user.password, current_password):
            return 'Current password is incorrect.'

        # Check if new passwords match
        if new_password != confirm_password:
            return 'New passwords do not match.'

        # Hash the new password and update the user
        current_user.password = generate_password_hash(
            new_password, method='pbkdf2:sha256', salt_length=8
        )

        try:
            db.session.commit()  # Save the updated password to the database
            return 'Password changed successfully.'
        except Exception as e:
            return f'There was an issue changing your password: {e}'

    return render_template('admin/admin_change_password.html')


@bp.route('/admin/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    # Check if the current user is an admin and a super admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin
    if not current_user.is_super_admin:
        return "You do not have permission to add a new admin."

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        shift = request.form['shift']
        prenom = request.form['prenom']
        matricule = request.form['matricule']
        fonction = request.form['fonction']
        password = request.form['password']
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=8
        )

        # Check for existing user by username, email, or phone
        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email) |
            (User.phone == phone) |
            (User.matricule == matricule)
        ).first()

        if existing_user:
            return 'Username, email, or phone already exists. Please choose another.'

        # Create new admin
        new_admin = User(
            username=username,
            email=email,
            matricule=matricule,
            shift=shift,
            phone=phone,
            fonction=fonction,
            prenom=prenom,
            password=hashed_password,
            is_admin=True
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            return redirect(url_for('admin.admin'))
        except Exception as e:
            return f'There was an issue creating the admin: {e}'

    return render_template('admin/add_admin.html')


@bp.route('/admin/approve_user/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)

    if request.form['action'] == 'approve':
        # Assign the shift only if the user is approved
        shift = request.form.get('shift')
        if shift in ['A', 'B', 'C']:
            user.shift = shift
            user.is_approved = True
            user.is_pending = False  # Ensure the user is no longer pending
            db.session.commit()
            flash(
                f'User {user.username} approved and assigned to Shift {shift}.', 'success')
        else:
            flash('Invalid shift selection.', 'danger')

    elif request.form['action'] == 'reject':
        # If the user is rejected, remove them from the database
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been rejected.', 'info')

    # Redirect back to the pending users page
    return redirect(url_for('admin.view_pending_users'))


@bp.route('/view_admins')
def view_admins():
    admins = User.query.filter_by(is_admin=True).all()
    return render_template('admin/admin_list.html', admins=admins)


@bp.route('/view_pending_users')
@login_required
def view_pending_users():
    # Ensure query only gets pending, unapproved users
    pending_users = User.query.filter_by(
        is_admin=False, is_approved=False, is_pending=True).all()
    return render_template('admin/pending_users.html', pending_users=pending_users)


@bp.route('/view_normal_users', methods=['GET', 'POST'])
@login_required
def view_normal_users():
    search_query = request.args.get('search', '')  # Get search query from URL
    page = request.args.get('page', 1, type=int)  # Get the current page

    # Base query for normal users
    query = User.query.filter_by(is_admin=False, is_approved=True)

    # Apply search filter if query is present
    if search_query:
        query = query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.matricule.ilike(f'%{search_query}%'))
        )

    # Paginate the results
    pagination = query.paginate(page=page, per_page=10)

    # Pass both normal_users and pagination to the template
    return render_template(
        'admin/normal_users.html',
        normal_users=pagination.items,
        search_query=search_query,
        pagination=pagination
    )


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')


@bp.route('/load_conference', methods=['GET', 'POST'])
@login_required
def load_conference():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part. Please choose a file to upload.')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file. Please choose a file to upload.')
            return redirect(request.url)

        if file and file.filename.lower().endswith(('.xlsx', '.xls')):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            uploaded_files = session.get('uploaded_files', [])
            uploaded_files.append(
                {'filename': filename, 'filepath': file_path,
                    'upload_time': upload_time}
            )
            session['uploaded_files'] = uploaded_files

            flash('File successfully uploaded and processed.')
            return redirect(url_for('admin.load_conference'))

        flash(
            'Invalid file type. Please upload an Excel file with .xlsx or .xls extension.')

    uploaded_files = session.get('uploaded_files', [])
    return render_template('admin/load_conference.html', user=current_user, uploaded_files=uploaded_files)


@bp.route('/open_file/<filename>', methods=['GET'])
@login_required
def open_file(filename):
    # Construct the file path
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        flash(f'File {filename} not found.')
        return redirect(url_for('admin.load_conference'))

    # Return the file for download
    try:
        return send_file(file_path)
    except Exception as e:
        flash(f'Error opening file: {str(e)}')
        return redirect(url_for('admin.load_conference'))


@bp.route('/conference', methods=['GET'])
@login_required
def conference():
    # Get the list of uploaded files from the session
    uploaded_files = session.get('uploaded_files', [])
    if not uploaded_files:
        flash('No uploaded conference files found.')

    # Render the 'conference.html' to list uploaded files
    return render_template('conference.html', user=current_user, uploaded_files=uploaded_files)


@bp.route('/download_conference/<filename>', methods=['GET'])
def download_conference(filename):
    # Construct the file path
    file_path = os.path.join(os.getcwd(), 'uploads', filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return "File not found", 404

    # Check the file extension and send the file as an attachment
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            print(f"Error sending file: {e}")
            return "Error sending file", 500
    else:
        return "Unsupported file format", 400


@bp.route('/statistiques_admin')
@login_required
def statistiques_admin():
    # Get the selected filters from the form
    month_filter = request.args.get('month')
    year_filter = request.args.get('year')
    shift_filter = request.args.get('shift')
    Escale_filter = request.args.get('Escale')
    marchandise_filter = request.args.get('marchandise')
    grue_filter = request.args.get('grue')

    # Query all validated tasks
    query = Todo.query.filter_by(status='Validated')

    # Apply filters if selected
    if month_filter:
        query = query.filter(db.extract(
            'month', Todo.date_created) == month_filter)
    if year_filter:
        query = query.filter(db.extract(
            'year', Todo.date_created) == year_filter)
    if shift_filter:
        query = query.filter_by(shift=shift_filter)
    if Escale_filter:
        query = query.filter_by(Escale=Escale_filter)
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
    available_years = sorted(
        set(todo.date_created.year for todo in Todo.query.all()))

    # Fetch distinct values for the filters
    available_escales = sorted(
        set(todo.Escale for todo in Todo.query.all() if todo.Escale))
    available_marchandises = sorted(
        set(todo.marchandise for todo in Todo.query.all() if todo.marchandise))
    available_grues = sorted(
        set(todo.grue for todo in Todo.query.all() if todo.grue))

    # Pass month names and other data to the template
    return render_template('admin/admin_statistiques.html',
                           months=months,
                           task_counts=task_counts,
                           available_years=available_years,
                           available_escales=available_escales,
                           # Pass available Marchandise options
                           available_marchandises=available_marchandises,
                           available_grues=available_grues,  # Pass available Grue options
                           month_names=calendar.month_name,
                           stats=zip(months, task_counts))


@bp.route('/saisai_conference', methods=['GET', 'POST'])
def saisai_conference():
    if request.method == 'POST':
        try:
            # Retrieve form data for multiple lines
            postes = request.form.getlist('poste[]')
            pms = request.form.getlist('pm[]')
            navires = request.form.getlist('navire[]')
            marchandises = request.form.getlist('marchandise[]')
            tonnages_manif = request.form.getlist('tonnage_manif[]')
            tonnages_rest = request.form.getlist('tonnage_rest[]')
            consignataires = request.form.getlist('consignataire[]')
            receptionnaires = request.form.getlist('receptionnaire[]')
            grues = request.form.getlist('grue[]')
            elevateurs = request.form.getlist('elevateur[]')
            materiels_a_bord = request.form.getlist('materiel_a_bord[]')
            dates_debut_travail = request.form.getlist('Date_debut_travail[]')
            dates_fin_travail = request.form.getlist('Date_fin_travail[]')
            heures_terminaison_travail_prevues = request.form.getlist(
                'Heure_Terminaison_Travail_Prévue[]')
            observations = request.form.getlist('observation[]')

            # Ensure we have consistent data lengths
            num_conferences = len(postes)
            if not all(len(lst) == num_conferences for lst in [pms, navires, marchandises, tonnages_manif, tonnages_rest, consignataires, receptionnaires, grues, elevateurs, materiels_a_bord, dates_debut_travail, dates_fin_travail, heures_terminaison_travail_prevues, observations]):
                flash(
                    'Inconsistent number of inputs for multiple conferences.', 'danger')
                return redirect(url_for('admin.saisai_conference'))

            # Loop through the number of conferences to create
            for i in range(num_conferences):
                # Parse the date and time fields correctly
                Date_debut_travail = datetime.strptime(
                    dates_debut_travail[i], '%Y-%m-%d').date()
                Date_fin_travail = datetime.strptime(
                    dates_fin_travail[i], '%Y-%m-%d').date()

                Heure_Terminaison_Travail_Prévue = None
                if heures_terminaison_travail_prevues[i]:
                    try:
                        Heure_Terminaison_Travail_Prévue = datetime.strptime(
                            heures_terminaison_travail_prevues[i], '%H').time()
                    except ValueError:
                        flash(
                            f'Invalid time format for Heure Terminaison in row {i + 1}.', 'danger')
                        return redirect(url_for('admin.saisai_conference'))

                # Create a new Conference object for each set of data
                new_conference = Conference(
                    poste=postes[i],
                    pm=pms[i],
                    navire=navires[i],
                    marchandise=marchandises[i],
                    tonnage_manif=tonnages_manif[i],
                    tonnage_rest=tonnages_rest[i],
                    consignataire=consignataires[i],
                    receptionnaire=receptionnaires[i],
                    grue=grues[i],
                    elevateur=elevateurs[i],
                    materiel_a_bord=materiels_a_bord[i],
                    Date_debut_travail=Date_debut_travail,
                    Date_fin_travail=Date_fin_travail,
                    Heure_Terminaison_Travail_Prévue=Heure_Terminaison_Travail_Prévue,
                    observation=observations[i]
                )

                # Save the conference to the database
                db.session.add(new_conference)

            # Commit the session after adding all conferences
            db.session.commit()

            flash(f'{num_conferences} Conferences added successfully!', 'success')
            return redirect(url_for('admin.saisai_conference'))

        except Exception as e:
            # Handle exceptions with a flash message
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('admin.saisai_conference'))

    # If it's a GET request, display the form
    return render_template('admin/saisai_conference.html')


@bp.route('/conference1', methods=['GET', 'POST'])
def conference1():
    # Get the conference_id from the request args
    conference_id = request.args.get('conference_id')
    print(f"Requested conference_id: {conference_id}")
    conference = Conference.query.get(conference_id)

    if not conference:
        return 'Conference not found.', 404

    if request.method == 'POST':
        # Process form data for updating the conference
        poste = request.form.get('poste')
        pm = request.form.get('pm')
        Navire = request.form.get('Navire')
        Marchandise = request.form.get('Marchandise')
        Tonnage_manif = request.form.get('Tonnage manif')
        Tonnage_rest = request.form.get('Tonnage Rest')
        Consignataire = request.form.get('Consignataire')
        Receptionnaire = request.form.get('Réceptionnaire')
        grue = request.form.get('grue')
        elevateur = request.form.get('elevateur')
        Materiel_a_bord = request.form.get('Materiel a bord')
        Date_debut_travail = request.form.get('Date_debut_travail')
        Date_fin_travail = request.form.get('Date_fin_travail')
        Heure_terminaison_travail = request.form.get(
            'Heure_Terminaison Travail Prévue')
        observation = request.form.get('observation')

        # Validate required fields
        if not all([poste, pm, Navire, Tonnage_manif, Tonnage_rest, Consignataire, Receptionnaire, grue, elevateur, Materiel_a_bord, Date_debut_travail, Date_fin_travail, Heure_terminaison_travail, observation]):
            return 'All fields are required.'

        # Update the existing conference object with the new data
        conference.poste = poste
        conference.pm = pm
        conference.Navire = Navire
        conference.Marchandise = Marchandise
        conference.Tonnage_manif = Tonnage_manif
        conference.Tonnage_rest = Tonnage_rest
        conference.Consignataire = Consignataire
        conference.Receptionnaire = Receptionnaire
        conference.grue = grue
        conference.elevateur = elevateur
        conference.Materiel_a_bord = Materiel_a_bord
        conference.Date_debut_travail = Date_debut_travail
        conference.Date_fin_travail = Date_fin_travail
        conference.Heure_terminaison_travail = Heure_terminaison_travail
        conference.observation = observation

        try:
            # Commit the changes to the database
            db.session.commit()
            return redirect(url_for('admin.conference1', conference_id=conference.id))
        except Exception as e:
            return f'There was an issue updating the conference: {e}'

    # Render the template with the conference data for GET request
    return render_template('admin/conference1.html', conference=conference)


@bp.route('/all_conferences')
@login_required
def all_conferences():
    # Query all conferences from the database
    # Ensure you have the Conference model imported
    conferences = Conference.query.all()
    return render_template('admin/all_conferences.html', conferences=conferences)


@bp.route('/delete_conference/<int:conference_id>', methods=['POST'])
@login_required
def delete_conference(conference_id):
    conference = Conference.query.get(conference_id)
    if conference:
        db.session.delete(conference)
        db.session.commit()
        flash('Conference deleted successfully!', 'success')
    else:
        flash('Conference not found.', 'error')
    return redirect(url_for('admin.all_conferences'))


@bp.route('/get_file_path/<path:filename>', methods=['GET'])
@login_required
def get_file_path(filename):
    # Construct the file path
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Check if the file exists
    if os.path.exists(file_path):
        return f'The absolute path for the uploaded file is: {file_path}'
    else:
        return 'File not found.', 404
