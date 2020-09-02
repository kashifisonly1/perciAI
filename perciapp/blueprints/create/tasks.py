import random as random
from sqlalchemy import update
from perciapp.extensions import db
from perciapp.app import create_celery_app
from perciapp.blueprints.create.helper import generate
from perciapp.blueprints.create.models.create import Create

celery = create_celery_app()


@celery.task()
def generate_sent1(description_id):
    """
    Create description from text inputs and save description into database.
    """
    #getting the description from postgres
    import random
    description = Create.query.get(description_id)

    #loading in description inputs
    title = description.title
    gender = description.gender
    category = description.category
    subcategory = description.subcategory
    detail1 = description.detail1
    detail2 = description.detail2
    detail3 = description.detail3
    detail4 = description.detail4
    detail5 = description.detail5

    #concatenating the category item
    cat = gender + '/' + category + '/' + subcategory
        
    #concatenating details into features list
    features = []
    for detail in [detail1, detail2, detail3, detail4, detail5]:
        if len(detail) > 1:
            features.append(detail)

    #inputs to LM
    args = {}
    args["model_type"]='gpt2'
    args['model_name_or_path']= 'perciapp/models/womens_clothing_description_beginning'
    args['padding_text']= ''
    args['length']=45
    args['temperature']=1.0
    args['top_k']=0
    args['top_p']=0.9
    args['no_cuda']=False
    args['seed']= random.randint(1,100001)

    features = ' - '.join(features)

    args['prompt'] = '<bos> <category> ' + str(category) + ' <features> ' + features + ' <brand> <model> ' + title + '\t<desc1> '

    sent1 = generate(args)[0]

    update = Create.query.filter_by(id=description_id).update({'sent1':sent1})
    db.session.commit()

@celery.task()
def generate_sent2(description_id):
    """
    Create description from text inputs and save description into database.
    """
    import random
    description = Create.query.get(description_id)

    #loading in description inputs
    title = description.title
    gender = description.gender
    category = description.category
    subcategory = description.subcategory
    detail1 = description.detail1
    detail2 = description.detail2
    detail3 = description.detail3
    detail4 = description.detail4
    detail5 = description.detail5

    #concatenating the category item
    cat = gender + '/' + category + '/' + subcategory
        
    #concatenating details into features list
    features = []
    for detail in [detail1, detail2, detail3, detail4, detail5]:
        if len(detail) > 1:
            features.append(detail)

    #inputs to LM
    args = {}
    args["model_type"]='gpt2'
    args['model_name_or_path']= 'perciapp/models/womens_clothing_description_middle'
    args['padding_text']= ''
    args['length']=45
    args['temperature']=1.0
    args['top_k']=0
    args['top_p']=0.9
    args['no_cuda']=False
    args['seed']= random.randint(1,100001)

    features = ' - '.join(features)

    args['prompt'] = '<bos> <category> ' + str(category) + ' <features> ' + features + ' <brand> <model> ' + title + '\t<middle> '

    sent2 = generate(args)[0]

    update = Create.query.filter_by(id=description_id).update({'sent2':sent2})
    db.session.commit()

@celery.task()
def generate_sent3(description_id):
    """
    Create description from text inputs and save description into database.
    """
    #getting the description from postgres
    import random
    description = Create.query.get(description_id)

    #loading in description inputs
    title = description.title
    gender = description.gender
    category = description.category
    subcategory = description.subcategory
    detail1 = description.detail1
    detail2 = description.detail2
    detail3 = description.detail3
    detail4 = description.detail4
    detail5 = description.detail5

    #concatenating the category item
    cat = gender + '/' + category + '/' + subcategory
        
    #concatenating details into features list
    features = []
    for detail in [detail1, detail2, detail3, detail4, detail5]:
        if len(detail) > 1:
            features.append(detail)

    #inputs to LM
    args = {}
    args["model_type"]='gpt2'
    args['model_name_or_path']= 'perciapp/models/womens_clothing_description_end'
    args['padding_text']= ''
    args['length']=45
    args['temperature']=1.0
    args['top_k']=0
    args['top_p']=0.9
    args['no_cuda']=False
    args['seed']= random.randint(1,100001)

    features = ' - '.join(features)
    args['prompt'] = '<bos> <category> ' + str(category) + ' <features> ' + features + ' <brand> <model> ' + title + '\t<end> '

    sent3 = generate(args)[0]
    
    update = Create.query.filter_by(id=description_id).update({'sent3':sent3})
    db.session.commit()
    
    return None
