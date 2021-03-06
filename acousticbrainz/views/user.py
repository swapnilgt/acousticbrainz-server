from flask import Blueprint, render_template
from flask_login import current_user
from acousticbrainz.data import user as user_data, dataset
from werkzeug.exceptions import NotFound

user_bp = Blueprint('user', __name__)


@user_bp.route('/<musicbrainz_id>/')
def profile(musicbrainz_id):
    if current_user.is_authenticated() and \
       current_user.musicbrainz_id == musicbrainz_id:
        user = current_user
    else:
        user = user_data.get_by_mb_id(musicbrainz_id)
        if user is None:
            raise NotFound("Can't find this user.")

    return render_template(
        'user/profile.html',
        user=user,
        datasets=dataset.get_by_user_id(user.id)
    )
