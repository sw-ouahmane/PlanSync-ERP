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

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get = 'infos.ouahmane@gmail.com'
    MAIL_PASSWORD = os.environ.get = 'hxur bbzh nswa twdo'
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    DEBUG = True


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
