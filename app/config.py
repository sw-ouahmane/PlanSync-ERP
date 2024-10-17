import os


class Config:
    SECRET_KEY = os.environ.get(
        'f9b7e53d705071997a5da4d1b8513479') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # or \ 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Set the upload folder path
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # This will be set in your environment
    MAIL_USERNAME = os.environ.get('infos.ouahmane@gmail.com')
    # This will be set in your environment
    MAIL_PASSWORD = os.environ.get('hxur bbzh nswa twdo')
    # This will be set in your environment
    MAIL_DEFAULT_SENDER = os.environ.get('infos.ouahmane@gmail.com')


# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay
# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay
SQLALCHEMY_DATABASE_URI = 'postgresql: // plansync_erp_l4ay_user: zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay'


# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay


# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay

# set DATABASE_URL=postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay?sslmode=require
# set MAIL_USERNAME=infos.ouahmane@gmail.com
# set MAIL_PASSWORD=hxur bbzh nswa twdo
# set MAIL_DEFAULT_SENDER=infos.ouahmane@gmail.com
# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a/plansync_erp_l4ay
