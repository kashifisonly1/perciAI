from flask import jsonify
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
    args['prompt']=""
    args['padding_text']= ''
    args['length']=45
    args['temperature']=1.0
    args['top_k']=0
    args['top_p']=0.9
    args['no_cuda']=False
    args['seed']=1

    features = ' - '.join(features)

    args['prompt'] = '<bos> <category> ' + str(category) + ' <features> ' + features + ' <brand> <model> ' + title + '\t<desc1> '

    output = generate(args)[0]

    description.description = output

    description.save()
