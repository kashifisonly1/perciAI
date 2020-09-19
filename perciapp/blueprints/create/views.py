from flask import (
    Blueprint, 
    current_app, 
    render_template, 
    request, 
    redirect,
    flash,
    jsonify,
    url_for)

from flask_login import current_user, login_required

from lib.util_json import render_json
from perciapp.extensions import limiter
from perciapp.blueprints.create.decorators import credits_required
from perciapp.blueprints.create.forms import CreateForm
from perciapp.blueprints.create.models.create import Create
from lib.subcategories import Subcategories
from celery import group
import json

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

        from perciapp.blueprints.create.tasks import (
            generate_sent1,
            generate_sent2,
            generate_sent3,
            edit_sent1,
            edit_sent2,
            edit_sent3,
            error_edit_sent1,
            error_edit_sent2,
            error_edit_sent3)

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
            error = 'You need more credits, Honey Bun.'
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
        first = ['sent1', 'sent1_2', 'sent1_3', 'sent1_4', 'sent1_5',
        'sent1_6', 'sent1_7', 'sent1_8', 'sent1_9']
        second = ['sent2', 'sent2_2', 'sent2_3', 'sent2_4', 'sent2_5',
        'sent2_6', 'sent2_7', 'sent2_8', 'sent2_9']
        third = ['sent3', 'sent3_2', 'sent3_3', 'sent3_4', 'sent3_5',
        'sent3_6', 'sent3_7', 'sent3_8', 'sent3_9']
        
        # #generate the first sentences

        from celery import chord
        callback = edit_sent1.s().set(link_error=[error_edit_sent1.s()])
        tasks = [generate_sent1.s(create.id, label) for label in first]
        chord(tasks)(callback)

        callback = edit_sent2.s().set(link_error=[error_edit_sent2.s()])
        tasks = [generate_sent2.s(create.id, label) for label in second]
        chord(tasks)(callback)
        
        callback = edit_sent3.s().set(link_error=[error_edit_sent3.s()])
        tasks = [generate_sent3.s(create.id, label) for label in third]
        chord(tasks)(callback)

        flash('Success! Your description will appear in a few seconds.', 'success')

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

