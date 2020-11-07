from flask import (
    Blueprint,
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
from google.cloud import pubsub_v1

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

        print()
        print('post method starting now')
        print()

        from perciapp.blueprints.create.tasks import(
            generate_sent1,
            generate_sent2,
            generate_sent3,
            edit_sent1,
            edit_sent2,
            edit_sent3
        )



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
            error = 'You need more credits.'
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

        first = ['sent1', 'sent1_2', 'sent1_3', 'sent1_4', 'sent1_5',
                 'sent1_6', 'sent1_7', 'sent1_8', 'sent1_9', 'sent1_10',
                 'sent1_11', 'sent1_12', 'sent1_13', 'sent1_14', 'sent1_15',
                 'sent1_16', 'sent1_17', 'sent1_18', 'sent1_19']
        second = ['sent2', 'sent2_2', 'sent2_3', 'sent2_4', 'sent2_5',
                  'sent2_6', 'sent2_7', 'sent2_8', 'sent2_9', 'sent2_10',
                  'sent2_11', 'sent2_12', 'sent2_13', 'sent2_14', 'sent2_15',
                  'sent2_16', 'sent2_17', 'sent2_18', 'sent2_19']
        third = ['sent3', 'sent3_2', 'sent3_3', 'sent3_4', 'sent3_5',
                 'sent3_6', 'sent3_7', 'sent3_8', 'sent3_9', 'sent3_10',
                 'sent3_11', 'sent3_12', 'sent3_13', 'sent3_14', 'sent3_15',
                 'sent3_16', 'sent3_17', 'sent3_18', 'sent3_19']

        project_id = "perciapp"
        topic_id = "description-order"

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)

        for i in ['sent1', 'sent1_2']:
            data = str(create.id)
            data = data.encode("utf-8")
            future = publisher.publish(topic_path, data, label=i)
            print(future.result())

        print()
        print()
        print(f"Published messages to {topic_path}.")
        print()
        print()

        # generate sentences
        # for label in first:
        #     #THIS WILL BE REPLACED BY CALLS TO PUB/SUB
        #     generate_sent1(create.id, label)

        # for label in second:
        #     #THIS WILL BE REPLACED BY CALLS TO PUB/SUB
        #     generate_sent2(create.id, label)

        # for label in third:
        #     #THIS WILL BE REPLACED BY CALLS TO PUB/SUB
        #     generate_sent3(create.id, label)

        # edit_sent1(create.id)
        # edit_sent2(create.id)
        # edit_sent3(create.id)

        flash('Success! Your description will appear in a few seconds.',
              'success')

        return redirect(url_for('create.create_description'))
    else:
        recent_descriptions = Create.query.filter\
            (Create.user_id == current_user.id) \
            .order_by(Create.created_on.desc()).limit(5)

        return render_template('create/create_description.html',
                               form=form,
                               recent_descriptions=recent_descriptions)


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

    return render_template('create/history.html',
                           descriptions=paginated_descriptions)

@create.route('/gensent1', methods=['POST'])
@csrf.exempt
def index():
    message = request.get_json()['message']
    print()
    print()
    print('receiving route starting now')
    print()
    print()
    description_id = int(base64.b64decode(message.data).decode('utf-8').strip())
    print()
    print()
    print('description_id=')
    print(description_id)
    label = message.attributes.get('label')
    print()
    print()
    print('label=')
    print(label)
    print()
    print()
    print()
    id = generate_sent1(description_id,label)
    return ('', 204)

# @create.route('/gensent1-2', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_2')
#     return ('', 204)

# @create.route('/gensent1-3', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_3')
#     return ('', 204)

# @create.route('/gensent1-4', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_4')
#     return ('', 204)

# @create.route('/gensent1-5', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_5')
#     return ('', 204)

# @create.route('/gensent1-6', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_6')
#     return ('', 204)

# @create.route('/gensent1-7', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_7')
#     return ('', 204)

# @create.route('/gensent1-8', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_8')
#     return ('', 204)

# @create.route('/gensent1-9', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_9')
#     return ('', 204)

# @create.route('/gensent1-10', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_10')
#     return ('', 204)

# @create.route('/gensent1-11', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_11')
#     return ('', 204)

# @create.route('/gensent1-12', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_12')
#     return ('', 204)

# @create.route('/gensent1-13', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_13')
#     return ('', 204)

# @create.route('/gensent1-14', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_14')
#     return ('', 204)

# @create.route('/gensent1-15', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_15')
#     return ('', 204)

# @create.route('/gensent1-16', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_16')
#     return ('', 204)

# @create.route('/gensent1-17', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_17')
#     return ('', 204)

# @create.route('/gensent1-18', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_18')
#     return ('', 204)

# @create.route('/gensent1-19', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent1(description_id,'sent1_19')
#     return ('', 204)

# @create.route('/gensent2-1', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2')
#     return ('', 204)

# @create.route('/gensent2-2', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_2')
#     return ('', 204)

# @create.route('/gensent2-3', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_3')
#     return ('', 204)

# @create.route('/gensent2-4', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_4')
#     return ('', 204)

# @create.route('/gensent2-5', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_5')
#     return ('', 204)

# @create.route('/gensent2-6', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_6')
#     return ('', 204)

# @create.route('/gensent2-7', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_7')
#     return ('', 204)

# @create.route('/gensent2-8', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_8')
#     return ('', 204)

# @create.route('/gensent2-9', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_9')
#     return ('', 204)

# @create.route('/gensent2-10', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_10')
#     return ('', 204)

# @create.route('/gensent2-11', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_11')
#     return ('', 204)

# @create.route('/gensent2-12', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_12')
#     return ('', 204)

# @create.route('/gensent2-13', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_13')
#     return ('', 204)

# @create.route('/gensent2-14', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_14')
#     return ('', 204)

# @create.route('/gensent2-15', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_15')
#     return ('', 204)

# @create.route('/gensent2-16', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_16')
#     return ('', 204)

# @create.route('/gensent2-17', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_17')
#     return ('', 204)

# @create.route('/gensent2-18', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_18')
#     return ('', 204)

# @create.route('/gensent2-19', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent2(description_id,'sent2_19')
#     return ('', 204)

# @create.route('/gensent3-1', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3')
#     return ('', 204)

# @create.route('/gensent3-2', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_2')
#     return ('', 204)

# @create.route('/gensent3-3', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_3')
#     return ('', 204)

# @create.route('/gensent3-4', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_4')
#     return ('', 204)

# @create.route('/gensent3-5', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_5')
#     return ('', 204)

# @create.route('/gensent3-6', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_6')
#     return ('', 204)

# @create.route('/gensent3-7', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_7')
#     return ('', 204)

# @create.route('/gensent3-8', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_8')
#     return ('', 204)

# @create.route('/gensent3-9', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_9')
#     return ('', 204)

# @create.route('/gensent3-10', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_10')
#     return ('', 204)

# @create.route('/gensent3-11', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_11')
#     return ('', 204)

# @create.route('/gensent3-12', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_12')
#     return ('', 204)

# @create.route('/gensent3-13', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_13')
#     return ('', 204)

# @create.route('/gensent3-14', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_14')
#     return ('', 204)

# @create.route('/gensent3-15', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_15')
#     return ('', 204)

# @create.route('/gensent3-16', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_16')
#     return ('', 204)

# @create.route('/gensent3-17', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_17')
#     return ('', 204)

# @create.route('/gensent3-18', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_18')
#     return ('', 204)

# @create.route('/gensent3-19', methods=['POST'])
# def index():
#     description_id = request.get_json()['description_id']
#     generate_sent3(description_id,'sent3_19')
#     return ('', 204)

# @create.route('/editsent3')
# def editThird(description_id):
#     #Pick the best third sentence
#     edit_sent3(description_id)
#     return description_id
