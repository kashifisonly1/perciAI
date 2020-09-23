import random as random
from perciapp.extensions import db
from perciapp.app import create_celery_app
from perciapp.blueprints.create.helper import (
    generate,
    format_inputs,
    args,
    brand_remove,
    score,
    pop_best_sentence,
    return_most_similar)

from perciapp.blueprints.create.models.create import Create

celery = create_celery_app()


def remove_bad_sentences(descriptions):
    # remove empty sentence from killed processes in the description list
    for item in descriptions:
        if type(item) != str:
            descriptions.remove(item)
        # remove shitty generations that are
        # feature inputs instead of sentences - possible bug causing it
        elif item.startswith('Length'):
            descriptions.remove(item)
    return descriptions


@celery.task()
def generate_sent1(description_id, label):
    """
    Create description from text inputs and save description into database.
    """
    # getting the description inputs
    title, cat, features = format_inputs(Create.query.get(description_id))

    # inputs to LM
    if 'shoes' in cat.lower():
        model = 'perciapp/models/unisex_shoes_description_beginning'
        args['model_name_or_path'] = model
    elif cat.lower().startswith('men'):
        model = 'perciapp/models/mens_clothing_description_beginning'
        args['model_name_or_path'] = model
    else:
        model = 'perciapp/models/womens_clothing_description_beginning'
        args['model_name_or_path'] = model

    args['seed'] = random.randint(1, 100001)
    args['prompt'] = f'<bos> <category> {cat} <features> \
                        {features} <brand> <model> {title} \t<desc1> '

    sent = brand_remove(generate(args)[0], title)

    if len(sent) > 199:
        sent = sent[:190]

    update = Create.query.filter_by(id=description_id).update({label: sent})
    db.session.commit()
    return description_id


@celery.task()
def generate_sent2(description_id, label):
    """
    Create description from text inputs and save description into database.
    """
    # getting the description inputs
    title, cat, features = format_inputs(Create.query.get(description_id))

    # inputs to LM
    if 'shoes' in cat.lower():
        model = 'perciapp/models/unisex_shoes_description_middle'
        args['model_name_or_path'] = model
    elif cat.lower().startswith('men'):
        model = 'perciapp/models/mens_clothing_description_middle'
        args['model_name_or_path'] = model
    else:
        model = 'perciapp/models/womens_clothing_description_middle'
        args['model_name_or_path'] = model

    args['seed'] = random.randint(1, 100001)
    args['prompt'] = f'<bos> <category> {cat} <features> \
                        {features} <brand> <model> {title} \t<middle> '

    sent = generate(args)[0]

    if len(sent) > 199:
        sent = sent[:190]

    update = Create.query.filter_by(id=description_id).update({label: sent})
    db.session.commit()
    return description_id


@celery.task()
def generate_sent3(description_id, label):
    """
    Create description from text inputs and save description into database.
    """
    # getting the description inputs
    title, cat, features = format_inputs(Create.query.get(description_id))

    # inputs to LM
    if 'shoes' in cat.lower():
        model = 'perciapp/models/unisex_shoes_description_end'
        args['model_name_or_path'] = model
    elif cat.lower().startswith('men'):
        model = 'perciapp/models/mens_clothing_description_end'
        args['model_name_or_path'] = model
    else:
        model = 'perciapp/models/womens_clothing_description_end'
        args['model_name_or_path'] = model

    args['seed'] = random.randint(1, 100001)
    args['prompt'] = f'<bos> <category> {cat} <features> \
                        {features} <brand> <model> {title} \t<end> '

    sent = generate(args)[0]

    if len(sent) > 199:
        sent = sent[:190]

    update = Create.query.filter_by(id=description_id).update({label: sent})
    db.session.commit()
    return description_id


@celery.task()
def edit_sent1(ids):
    """
    Cull sent1 candidates and put best candidate back into database
    """
    print()
    print()
    print('THIS IS THE EDIT FUNCTION NOW')
    print()
    print()

    # initialize model
    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # load in sentence candidates
    description = Create.query.get(ids[0])
    sent1 = description.sent1
    sent2 = description.sent1_2
    sent3 = description.sent1_3
    sent4 = description.sent1_4
    sent5 = description.sent1_5
    sent6 = description.sent1_6
    sent7 = description.sent1_7
    sent8 = description.sent1_8
    sent9 = description.sent1_9

    print()
    print()
    print('sentences:')
    print(sent1)
    print(sent2)
    print(sent3)
    print(sent4)
    print(sent5)
    print(sent6)
    print(sent7)
    print(sent8)
    print(sent9)
    print()
    print()

    descriptions = [sent1, sent2, sent3, sent4,
                    sent5, sent6, sent7, sent8, sent9]

    descriptions = remove_bad_sentences(descriptions)

    # remove 1st sentences without the product title in them
    for item in descriptions:
        if str(description.title) not in item:
            descriptions.remove(item)

    print()
    print()
    print('descriptions after edit:')
    print(descriptions)
    print()
    print()

    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores:')
    print(scores)
    print()
    print()
    # getting the description inputs
    title, cat, features = format_inputs(description)

# candidate1, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# candidate2, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# first_sent = return_most_similar(features,
#                                  [candidate1, candidate2])[0]

    index = scores.index(min(scores))
    first_sent = descriptions[index]

    update = Create.query.filter_by(id=ids[0]).update({'sent1': first_sent})
    db.session.commit()
    return None


@celery.task()
def error_edit_sent1(request, exc, traceback):
    """
    Cull sent1 candidates and put best candidate back into database
    """

    print()
    print()
    print('THIS IS THE ERROR_EDIT FUNCTION NOW')
    print()
    print()
    print('request.args[0][0] returns')
    print(request.args[0][0])
    print()
    print()
    # initialize model

    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # load in sentence candidates
    id = request.args[0][0]
    description = Create.query.get(id)
    sent1 = description.sent1
    sent2 = description.sent1_2
    sent3 = description.sent1_3
    sent4 = description.sent1_4
    sent5 = description.sent1_5
    sent6 = description.sent1_6
    sent7 = description.sent1_7
    sent8 = description.sent1_8
    sent9 = description.sent1_9

    print()
    print()
    print('sentences:')
    print(sent1)
    print(sent2)
    print(sent3)
    print(sent4)
    print(sent5)
    print(sent6)
    print(sent7)
    print(sent8)
    print(sent9)
    print()
    print()

    descriptions = [sent1, sent2, sent3, sent4, sent5,
                    sent6, sent7, sent8, sent9]

    descriptions = remove_bad_sentences(descriptions)

    # remove 1st sentences without the product title in them
    for item in descriptions:
        if str(description.title) not in item:
            descriptions.remove(item)

    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores:')
    print(scores)
    print()
    print()
    # getting the description inputs
    title, cat, features = format_inputs(Create.query.get(id))

# candidate1, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# candidate2, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# first_sent = return_most_similar(features,
#                                  [candidate1, candidate2])[0]

    index = scores.index(min(scores))
    first_sent = descriptions[index]

    update = Create.query.filter_by(id=id).update({'sent1': first_sent})
    db.session.commit()
    return None


@celery.task()
def edit_sent2(ids):
    """
    Cull sent1 candidates and put best candidate back into database
    """
    print()
    print()
    print('THIS IS THE EDIT FUNCTION NOW')
    print()
    print()

    # initialize model
    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # load in sentence candidates
    description = Create.query.get(ids[0])
    sent1 = description.sent2
    sent2 = description.sent2_2
    sent3 = description.sent2_3
    sent4 = description.sent2_4
    sent5 = description.sent2_5
    sent6 = description.sent2_6
    sent7 = description.sent2_7
    sent8 = description.sent2_8
    sent9 = description.sent2_9
    
    print()
    print()
    print('sentences:')
    print(sent1)
    print(sent2)
    print(sent3)
    print(sent4)
    print(sent5)
    print(sent6)
    print(sent7)
    print(sent8)
    print(sent9)
    print()
    print()

    descriptions = [sent1, sent2, sent3, sent4, sent5,
                    sent6, sent7, sent8, sent9]

    descriptions = remove_bad_sentences(descriptions)
             
    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores:')
    print(scores)
    print()
    print()
    # getting the description inputs
    title, cat, features = format_inputs(description)

# candidate1, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# candidate2, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# first_sent = return_most_similar(features,
#                                  [candidate1, candidate2])[0]

    index = scores.index(min(scores))
    sent = descriptions[index]

    update = Create.query.filter_by(id=ids[0]).update({'sent2': sent})
    db.session.commit()
    return None


@celery.task()
def error_edit_sent2(request, exc, traceback):
    """
    Cull sent1 candidates and put best candidate back into database
    """

    print()
    print()
    print('THIS IS THE ERROR_EDIT FUNCTION NOW')
    print()
    print()
    print('request.args[0][0] returns')
    print(request.args[0][0])
    print()
    print()
    # initialize model

    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # load in sentence candidates
    id = request.args[0][0]
    description = Create.query.get(id)
    sent1 = description.sent2
    sent2 = description.sent2_2
    sent3 = description.sent2_3
    sent4 = description.sent2_4
    sent5 = description.sent2_5
    sent6 = description.sent2_6
    sent7 = description.sent2_7
    sent8 = description.sent2_8
    sent9 = description.sent2_9
    
    print()
    print()
    print('sentences:')
    print(sent1)
    print(sent2)
    print(sent3)
    print(sent4)
    print(sent5)
    print(sent6)
    print(sent7)
    print(sent8)
    print(sent9)
    print()
    print()

    descriptions = [sent1, sent2, sent3, sent4, sent5,
                    sent6, sent7, sent8, sent9]

    descriptions = remove_bad_sentences(descriptions)
             
    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores:')
    print(scores)
    print()
    print()
    # getting the description inputs
    title, cat, features = format_inputs(Create.query.get(id))

    ## candidate1, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# candidate2, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# first_sent = return_most_similar(features,
#                                  [candidate1, candidate2])[0]

    index = scores.index(min(scores))
    sent = descriptions[index]

    update = Create.query.filter_by(id=id).update({'sent2': sent})
    db.session.commit()
    return None


@celery.task()
def edit_sent3(ids):
    """
    Cull sent1 candidates and put best candidate back into database
    """
    print()
    print()
    print('THIS IS THE EDIT FUNCTION NOW')
    print()
    print()

    # initialize model
    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # load in sentence candidates
    description = Create.query.get(ids[0])
    sent1 = description.sent3
    sent2 = description.sent3_2
    sent3 = description.sent3_3
    sent4 = description.sent3_4
    sent5 = description.sent3_5
    sent6 = description.sent3_6
    sent7 = description.sent3_7
    sent8 = description.sent3_8
    sent9 = description.sent3_9
    
    print()
    print()
    print('sentences:')
    print(sent1)
    print(sent2)
    print(sent3)
    print(sent4)
    print(sent5)
    print(sent6)
    print(sent7)
    print(sent8)
    print(sent9)
    print()
    print()

    descriptions = [sent1, sent2, sent3, sent4, sent5,
                    sent6, sent7, sent8, sent9]

    descriptions = remove_bad_sentences(descriptions)

    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores:')
    print(scores)
    print()
    print()
    # getting the description inputs
    title, cat, features = format_inputs(description)

# candidate1, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# candidate2, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# first_sent = return_most_similar(features,
#                                  [candidate1, candidate2])[0]

    index = scores.index(min(scores))
    sent = descriptions[index]

    update = Create.query.filter_by(id=ids[0]).update({'sent3': sent})
    db.session.commit()

    final_output = description.sent1 + ' ' + description.sent2 + ' ' + description.sent3
    update = Create.query.filter_by(id=ids[0]).update({'description':final_output})
    db.session.commit()
    return None


@celery.task()
def error_edit_sent3(request, exc, traceback):
    """
    Cull sent1 candidates and put best candidate back into database
    """

    print()
    print()
    print('THIS IS THE ERROR_EDIT FUNCTION NOW')
    print()
    print()
    print('request.args[0][0] returns')
    print(request.args[0][0])
    print()
    print()
    # initialize model

    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # load in sentence candidates
    id = request.args[0][0]
    description = Create.query.get(id)
    sent1 = description.sent3
    sent2 = description.sent3_2
    sent3 = description.sent3_3
    sent4 = description.sent3_4
    sent5 = description.sent3_5
    sent6 = description.sent3_6
    sent7 = description.sent3_7
    sent8 = description.sent3_8
    sent9 = description.sent3_9

    print()
    print()
    print('sentences:')
    print(sent1)
    print(sent2)
    print(sent3)
    print(sent4)
    print(sent5)
    print(sent6)
    print(sent7)
    print(sent8)
    print(sent9)
    print()
    print()

    descriptions = [sent1, sent2, sent3, sent4, sent5,
                    sent6, sent7, sent8, sent9]

    descriptions = remove_bad_sentences(descriptions)

    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores:')
    print(scores)
    print()
    print()
    # getting the description inputs
    title, cat, features = format_inputs(Create.query.get(id))

# candidate1, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# candidate2, descriptions, scores = pop_best_sentence(descriptions,
#                                                      scores)
# first_sent = return_most_similar(features,
#                                  [candidate1, candidate2])[0]

    index = scores.index(min(scores))
    sent = descriptions[index]

    update = Create.query.filter_by(id=id).update({'sent3': sent})
    db.session.commit()

    final_output = description.sent1 + '. ' + description.sent2 + '. ' + description.sent3 + '.'
    update = Create.query.filter_by(id=ids[0]).update({'description':final_output})
    db.session.commit()
    return None
