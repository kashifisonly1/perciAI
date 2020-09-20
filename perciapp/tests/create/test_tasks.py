from perciapp.extensions import mail
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
from perciapp.blueprints.user.models import User


class TestTasks(object):
    def test_input_format(self):
        """ Make sure the inputs are formatted correctly. """
        title = 'Air Jordans'
        gender = 'mens'
        category = 'shoes'
        subcategory = 'sneakers'
        detail1 = 'vamp straps'
        detail2 = 'open toe'
        detail3 = 'soft footbed'

        title, cat, features 

        cat = gender + '/' + category + '/' + subcategory
        
    #concatenating details into features list
    features = []
    for detail in [detail1, detail2, detail3, detail4, detail5]:
        if len(detail) > 1:
            features.append(detail)
    
    features = ' - '.join(features)

    return title, cat, features


    
    def test_generate_sentences(self):
        """ Deliver a password reset email. """
        with mail.record_messages() as outbox:
            user = User.find_by_identity('admin@local.host')
            deliver_password_reset_email(user.id, token)

            assert len(outbox) == 1
            assert token in outbox[0].body



        features = format_inputs(Create.query.get(description_id))
        title = 'Air Jordans'
        cat = 'mens/shoes/sneakers'
        
        features = 'vamp straps'
        detail2 = 'open toe'
        detail3 = 'soft footbed'
    #inputs to LM
    if 'shoes' in cat.lower():
        args['model_name_or_path']= 'perciapp/models/unisex_shoes_description_beginning'
    elif cat.lower().startswith('men'):
        args['model_name_or_path']= 'perciapp/models/mens_clothing_description_beginning'
    else:
        args['model_name_or_path']= 'perciapp/models/womens_clothing_description_beginning'
    
    args['seed']= random.randint(1,100001)
    args['prompt'] = f'<bos> <category> {cat} <features> {features} <brand> <model> {title} \t<desc1> '
    
    sent = brand_remove(generate(args)[0], title)

    if len(sent) > 199:
        sent = sent[:190]

    update = Create.query.filter_by(id=description_id).update({label:sent})
    db.session.commit()
    return description_id
