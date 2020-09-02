from flask import (
    Blueprint, 
    current_app, 
    render_template, 
    request, 
    jsonify, 
    redirect,
    flash,
    url_for)

from flask_login import current_user, login_required

from lib.util_json import render_json
from perciapp.extensions import limiter
from perciapp.blueprints.create.decorators import credits_required
from perciapp.blueprints.create.forms import CreateForm
from perciapp.blueprints.create.models.create import Create
from lib.subcategories import Subcategories
import json
import random
from perciapp.blueprints.create.helper import generate

create = Blueprint('create', __name__, template_folder='templates',
                url_prefix='/create')


@create.before_request
@login_required
def before_request():
    """ Protect all of the create endpoints. """
    pass

@create.route('/', methods=['GET', 'POST'])
@credits_required
@limiter.limit('3/second')
def create_description():

    form = CreateForm()

    if request.method == 'POST':

        from perciapp.blueprints.create.tasks import generate_sent1, generate_sent2, generate_sent3

        title = str(request.form.get('title'))
        gender = str(request.form.get('gender'))
        category = str(request.form.get('category'))
        subcategory = str(request.form.get('subcategory'))
        detail1 = request.form.get('detail1')
        detail2 = request.form.get('detail2')
        detail3 = request.form.get('detail3')
        detail4 = request.form.get('detail4')
        detail5 = request.form.get('detail5')

        if current_user.credits < 1:
            error = 'You need more credits bub.'
            return render_json(400, {'error': error})

        params = {
          'user_id': current_user.id,
          'title': title,
          'gender': gender,
          'category': category,
          'subcategory': subcategory,
          'detail1': detail1,
          'detail2': detail2,
          'detail3': detail3,
          'detail4': detail4,
          'detail5': detail5,
          'sent1': 'coming soon',
          'sent2': 'coming soon',
          'sent3': 'coming soon',
          'description': 'coming soon'
        }

        create = Create(**params)
        create.save_and_update_user(current_user)
        
        #generating the description in celery
        generate_sent1.delay(create.id)
        # generate_sent2.delay(create.id)
        # generate_sent3.delay(create.id)
        flash('Success! Your description will generate in a few seconds.', 'success')

        return redirect(url_for('create.create_description'))
    else:
        recent_descriptions = Create.query.filter(Create.user_id == current_user.id) \
            .order_by(Create.created_on.desc()).limit(5)

        return render_template('create/create_description.html', form=form, recent_descriptions=recent_descriptions)

@create.route('/create/subcategory/<category>')
def subcategory(category):

    return jsonify(Subcategories[category])

    # return jsonify({'subcategories' : subcategoryArray})

@create.route('/history', defaults={'page': 1})
@create.route('/history/page/<int:page>')
def history(page):
    paginated_descriptions = Create.query \
        .filter(Create.user_id == current_user.id) \
        .order_by(Create.created_on.desc()) \
        .paginate(page, 50, True)

    return render_template('create/history.html', descriptions=paginated_descriptions)

