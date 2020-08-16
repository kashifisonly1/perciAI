from flask import Blueprint, current_app, render_template, request, jsonify, redirect
from flask_login import current_user, login_required

from lib.util_json import render_json
from perciapp.extensions import limiter
from perciapp.blueprints.create.decorators import credits_required
from perciapp.blueprints.create.forms import CreateForm
from perciapp.blueprints.create.models.create import Create
from lib.subcategories import Subcategories

create = Blueprint('create', __name__, template_folder='templates',
                url_prefix='/create')


@create.before_request
@login_required
def before_request():
    """ Protect all of the create endpoints. """
    pass

@create.route('/create', methods=['GET', 'POST'])
@credits_required
@limiter.limit('3/second')
def create_description():
    
    if request.method == 'GET':
        recent_descriptions = Create.query.filter(Create.user_id == current_user.id) \
            .order_by(Create.created_on.desc()).limit(10)

        return render_template('create/create_description.html', recent_descriptions=recent_descriptions)

    form = CreateForm()

    # if request.method == 'POST':
    #     return '<h1>Category: {}, Subcategory: {}</h1>'.format(form.category.data, form.subcategory.data)

    # return render_template('create/create_description.html', form=form)

    if form.validate_on_submit():

        title = str(request.form.get('title'))
        gender = str(request.form.get('gender'))
        category = str(request.form.get('category'))
        subcategory = str(request.form.get('subcategory'))
        detail1 = list(request.form.get('detail1'))
        detail2 = list(request.form.get('detail2'))
        detail3 = list(request.form.get('detail3'))
        detail4 = list(request.form.get('detail4'))
        detail5 = list(request.form.get('detail5'))

        if current_user.credits < 1:
            error = 'You need more credits bub.'
            return render_json(400, {'error': error})
        
        description = Create.generate_description(title, gender, 
                            category, subcategory, detail1, detail2,
                            detail3, detail4, detail5)

        params = {
          'user_id': current_user.id,
          'title': title,
          'category': category,
          'subcategory': subcategory,
          'detail1': detail1,
          'detail2': detail2,
          'detail3': detail3,
          'detail4': detail4,
          'detail5': detail5,
          'description': description
        }

        create = Create(**params)
        create.save_and_update_user(current_user)

        return render_json(200, {'data': create.to_json()})
    else:
        return render_json(400,
                           {'error': 'You need to wager at least 1 credit.'})

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

