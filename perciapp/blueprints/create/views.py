from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    jsonify,
    url_for)

from perciapp.extensions import csrf

from flask_login import current_user, login_required

from lib.util_json import render_json
from perciapp.extensions import limiter
from perciapp.blueprints.create.decorators import credits_required
from perciapp.blueprints.create.forms import CreateForm
from perciapp.blueprints.create.models.create import Create
from lib.subcategories import Subcategories
from google.cloud import pubsub_v1
import base64
import requests
import os
import signal

create = Blueprint('create', __name__, template_folder='templates',
                   url_prefix='/create')


@create.route('/', methods=['GET', 'POST'])
@login_required
@limiter.limit('3/second')
def create_description():

    form = CreateForm()

    if request.method == 'POST':

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
            flash('You need more credits.','error')
            return redirect(url_for('create.create_description'))

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
          'description': 'coming soon'
        }

        create = Create(**params)
        create.save_and_update_user(current_user)

        firsts = ['sent1','sent1_2', 'sent1_3', 'sent1_4',
                  'sent1_5', 'sent1_6', 'sent1_7', 'sent1_8',
                  'sent1_9','sent1_10', 'sent1_11', 'sent1_12',
                  'sent1_13', 'sent1_14', 'sent1_15']

        seconds = ['sent2','sent2_2', 'sent2_3', 'sent2_4',
                  'sent2_5', 'sent2_6', 'sent2_7', 'sent2_8',
                  'sent2_9','sent2_10', 'sent2_11', 'sent2_12',
                  'sent2_13', 'sent2_14', 'sent2_15']

        thirds = ['sent3','sent3_2', 'sent3_3', 'sent3_4',
                  'sent3_5', 'sent3_6', 'sent3_7', 'sent3_8',
                  'sent3_9', 'sent3_10', 'sent3_11', 'sent3_12',
                  'sent3_13', 'sent3_14', 'sent3_15']

        project_id = "perciapp"
        topic_id = "description-order"

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)

        for i in firsts:
            data = str(create.id)
            data = data.encode("utf-8")
            future = publisher.publish(topic_path, data, label=i, id=str(create.id))
            print(future.result())

        topic_id = "description-order-sent-2"
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)
        
        for i in seconds:
            data = str(create.id)
            data = data.encode("utf-8")
            future = publisher.publish(topic_path, data, label=i, id=str(create.id))
            print(future.result())
        
        topic_id = "description-order-sent-3"
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)

        for i in thirds:
            data = str(create.id)
            data = data.encode("utf-8")
            future = publisher.publish(topic_path, data, label=i, id=str(create.id))
            print(future.result())

        print()
        print(f"Published sent_gen messages to {topic_path}.")
        print()

        #Send edit Pub/Sub message
        topic_id = "description-order-edit"
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)
        data = str(create.id)
        data = data.encode("utf-8")
        future = publisher.publish(topic_path, data)
        print(future.result())

        print()
        print(f"Published edit_sent message to {topic_path}.")
        print()

        flash('Huzzah! Your description will appear in about a minute when you refresh the page. Submit more items in the meantime.',
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
@login_required
def subcategory(category):

    return jsonify(Subcategories[category])


@create.route('/history', defaults={'page': 1})
@create.route('/history/page/<int:page>')
@login_required
def history(page):
    descriptions = Create.query \
        .filter(Create.user_id == current_user.id) \
        .order_by(Create.created_on.desc()) \
        .paginate(page, 50, True)

    return render_template('create/history.html',
                           descriptions=descriptions)

@create.route('/gensent1/', methods=['POST'])
@csrf.exempt
def routesent1():
    from perciapp.blueprints.create.tasks import generate_sent1
    message = request.get_json()['message']
    description_id = int(base64.b64decode(message['data']).decode('utf-8').strip())
    label = message['attributes']['label']
    generate_sent1(description_id,label)
    os.kill(os.getppid() , signal.SIGTERM)
    return ('', 204)

@create.route('/gensent2/', methods=['POST'])
@csrf.exempt
def routesent2():
    from perciapp.blueprints.create.tasks import generate_sent2
    message = request.get_json()['message']
    description_id = int(base64.b64decode(message['data']).decode('utf-8').strip())
    label = message['attributes']['label']
    generate_sent2(description_id,label)
    os.kill(os.getppid() , signal.SIGTERM)
    return ('', 204)

@create.route('/gensent3/', methods=['POST'])
@csrf.exempt
def routesent3():
    from perciapp.blueprints.create.tasks import generate_sent3
    message = request.get_json()['message']
    description_id = int(base64.b64decode(message['data']).decode('utf-8').strip())
    label = message['attributes']['label']
    generate_sent3(description_id,label)
    os.kill(os.getppid() , signal.SIGTERM)
    return ('', 204)

@create.route('/editsent1/', methods=['POST'])
@csrf.exempt
def routeedit1():
    from perciapp.blueprints.create.tasks import edit_sent1
    message = request.get_json()['message']
    description_id = int(base64.b64decode(message['data']).decode('utf-8').strip())
    id = edit_sent1(description_id)
    return ('', 204)

@create.route('/editsent2/', methods=['POST'])
@csrf.exempt
def routeedit2():
    from perciapp.blueprints.create.tasks import edit_sent2
    message = request.get_json()['message']
    description_id = int(base64.b64decode(message['data']).decode('utf-8').strip())
    id = edit_sent2(description_id)
    return ('', 204)

@create.route('/editsent3/', methods=['POST'])
@csrf.exempt
def routeedit3():
    from perciapp.blueprints.create.tasks import edit_sent3
    message = request.get_json()['message']
    description_id = int(base64.b64decode(message['data']).decode('utf-8').strip())
    id = edit_sent3(description_id)
    return ('', 204)

@create.route('/bulkprocess/', methods=['POST'])
@csrf.exempt
def bulkprocess():
    data = request.get_json()
    print('bulk POST request received:')
    print()
    print(data)
    print()

    title = data['title']
    gender = data['gender']
    category = data['category']
    subcategory = data['subcategory']
    detail1 = data['detail1']
    detail2 = data['detail2']
    detail3 = data['detail3']
    detail4 = data['detail4']
    detail5 = data['detail5']

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
        'description': 'coming soon'
    }

    create = Create(**params)
    create.save_and_update_user(current_user)

    firsts = ['sent1','sent1_2', 'sent1_3', 'sent1_4',
              'sent1_5', 'sent1_6', 'sent1_7', 'sent1_8',
              'sent1_9','sent1_10', 'sent1_11', 'sent1_12',
              'sent1_13', 'sent1_14', 'sent1_15']

    seconds = ['sent2','sent2_2', 'sent2_3', 'sent2_4',
               'sent2_5', 'sent2_6', 'sent2_7', 'sent2_8',
               'sent2_9','sent2_10', 'sent2_11', 'sent2_12',
               'sent2_13', 'sent2_14', 'sent2_15']

    thirds = ['sent3','sent3_2', 'sent3_3', 'sent3_4',
              'sent3_5', 'sent3_6', 'sent3_7', 'sent3_8',
              'sent3_9', 'sent3_10', 'sent3_11', 'sent3_12',
              'sent3_13', 'sent3_14', 'sent3_15']

    project_id = "perciapp"
    topic_id = "description-order"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    for i in firsts:
        data = str(create.id)
        data = data.encode("utf-8")
        future = publisher.publish(topic_path, data, label=i, id=str(create.id))
        print(future.result())

    topic_id = "description-order-sent-2"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    
    for i in seconds:
        data = str(create.id)
        data = data.encode("utf-8")
        future = publisher.publish(topic_path, data, label=i, id=str(create.id))
        print(future.result())
    
    topic_id = "description-order-sent-3"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    for i in thirds:
        data = str(create.id)
        data = data.encode("utf-8")
        future = publisher.publish(topic_path, data, label=i, id=str(create.id))
        print(future.result())

    print()
    print(f"Published sent_gen messages to {topic_path}.")
    print()

    #Send edit Pub/Sub message
    topic_id = "description-order-edit"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    data = str(create.id)
    data = data.encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(future.result())

    print()
    print(f"Published edit_sent message to {topic_path}.")
    print()

    #wait for 
    import time
    start = time.time()

    # repeatedly pull description until it has generated
    description = Create.query.get(create.id)
    output = [description.description]

    while output == 'coming soon':
        time.sleep(10)
        db.session.commit()
        description = Create.query.get(create.id)
        output = [description.description]
        now = time.time()
        print(description.title + ' bulk process waiting:' + str(int(now-start)))
        now = time.time()
        if now - start > 300:
            break
    
    from flask import jsonify
    return jsonify(title=title,description=output)