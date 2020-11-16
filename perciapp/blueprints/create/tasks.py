import random as random
import time
from perciapp.extensions import db
from perciapp.blueprints.create.helper import (
    generate,
    format_inputs,
    args,
    brand_remove,
    score,
    pop_best_sentence,
    return_most_similar)

from perciapp.blueprints.create.models.create import Create


def remove_bad_sentences(descriptions):
    # remove empty sentence from killed processes in the description list
    for item in descriptions:
        if type(item) != str:
            descriptions.remove(item)
        # remove shitty generations that are
        # feature inputs instead of sentences - possible bug causing it
        elif item.startswith('Length'):
            descriptions.remove(item)
        elif item.lower().startswith('our model'):
            descriptions.remove(item)
        elif len(item) < 15:
            descriptions.remove(item)
    return descriptions


def generate_sent1(description_id, label):
    """
    Create description from text inputs and save description into database.
    """
    print('generate_sent_1 starting now')

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
        sent = sent[:195]

    update = Create.query.filter_by(id=description_id).update({label: sent})
    db.session.commit()
    return description_id

def generate_sent2(description_id, label):
    """
    Create description from text inputs and save description into database.
    """
    print('generate_sent_2 starting now')

    # getting the description inputs
    title, cat, features = format_inputs(Create.query.get(description_id))

    # inputs to LM
    if 'shoes' in cat.lower():
        model = 'perciapp/models/unisex_shoes_description_middle'
        args['model_name_or_path'] = model
        #give shoes model extra length in case it creates new input
        args['length'] = 90
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

    # If model has started in <features> again, cut out extra input
    if '<middle>' in sent:
        sent = sent.split('<middle>')[1]

    if len(sent) > 199:
        sent = sent[:190]

    print('generation 2 complete')

    update = Create.query.filter_by(id=description_id).update({label: sent})
    db.session.commit()
    return description_id

def generate_sent3(description_id, label):
    """
    Create description from text inputs and save description into database.
    """
    print('generate_sent_3 starting now')

    # getting the description inputs
    title, cat, features = format_inputs(Create.query.get(description_id))

    # inputs to LM
    if 'shoes' in cat.lower():
        model = 'perciapp/models/unisex_shoes_description_end'
        args['model_name_or_path'] = model
        #give shoes model extra length in case it creates new input
        args['length'] = 90
    elif cat.lower().startswith('men'):
        model = 'perciapp/models/mens_clothing_description_end'
        args['model_name_or_path'] = model
    else:
        model = 'perciapp/models/womens_clothing_description_end'
        args['model_name_or_path'] = model

    args['seed'] = random.randint(1, 100001)
    args['prompt'] = f'<bos> <category> {cat} <features> \
                        {features} <brand> <model> {title} \t<end> '

    sent = brand_remove(generate(args)[0], title)

    # If model has started in <features> again, cut out extra input
    if '<end>' in sent:
        sent = sent.split('<end>')[1]

    if len(sent) > 199:
        sent = sent[:190]

    print('generation 3 complete')


    update = Create.query.filter_by(id=description_id).update({label: sent})
    db.session.commit()
    return description_id


def edit_sent1(id):
    """
    Cull sent1 candidates and put best candidate back into database
    """
    # initialize model
    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # repeatedly pull candidates until all have been generated
    description = Create.query.get(id)
    descriptions = [description.sent1, description.sent1_2, description.sent1_3,
                        description.sent1_4, description.sent1_5, description.sent1_6,
                        description.sent1_7, description.sent1_8, description.sent1_9,
                        description.sent1_10, description.sent1_11, description.sent1_12,
                        description.sent1_13, description.sent1_14, description.sent1_15,
                        description.sent1_16, description.sent1_17, description.sent1_18,
                        description.sent1_19]

    while None in descriptions:
        time.sleep(3)
        description = Create.query.get(id)
        descriptions = [description.sent1, description.sent1_2, description.sent1_3,
                        description.sent1_4, description.sent1_5, description.sent1_6,
                        description.sent1_7, description.sent1_8, description.sent1_9,
                        description.sent1_10, description.sent1_11, description.sent1_12,
                        description.sent1_13, description.sent1_14, description.sent1_15,
                        description.sent1_16, description.sent1_17, description.sent1_18,
                        description.sent1_19]

    print('edit_sent1 starting now')

    print('sentences:')
    for sentence in descriptions:
        print(sentence)
    print()

    descriptions = remove_bad_sentences(descriptions)

    # remove 1st sentences without the product title in them
    for item in descriptions:
        if str(description.title) not in item:
            descriptions.remove(item)

    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores/descriptions after edit:')
    for i, (desc, scr) in enumerate(zip(descriptions, scores)):
        print(int(scr), desc)

    # getting the description inputs
    title, cat, features = format_inputs(description)

    # pulling the best written sentence
    candidate1, descriptions, scores = pop_best_sentence(descriptions,
                                                        scores)
    print('candidate1:')
    print(candidate1)
    
    # pulling next best written sentence
    candidate2, descriptions, scores = pop_best_sentence(descriptions,
                                                        scores)
    print('candidate2:')
    print(candidate2)   

    # picking the one which is most similar to the features list
    first_sent = return_most_similar(features,
                                    [candidate1, candidate2])[0]

    print('winner:')
    print(first_sent)

    # saving the best first sentence
    update = Create.query.filter_by(id=id).update({'sent1_winner': first_sent})
    db.session.commit()
    print()
    print('edit_sent1 complete')
    return id

def edit_sent2(id):
    """
    Cull sent2 candidates and put best candidate into database
    """
    # initialize model
    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # repeatedly pull candidates until all have been generated
    description = Create.query.get(id)
    descriptions = [description.sent2, description.sent2_2, description.sent2_3,
                        description.sent2_4, description.sent2_5, description.sent2_6,
                        description.sent2_7, description.sent2_8, description.sent2_9,
                        description.sent2_10, description.sent2_11, description.sent2_12,
                        description.sent2_13, description.sent2_14, description.sent2_15,
                        description.sent2_16, description.sent2_17, description.sent2_18,
                        description.sent2_19]

    while None in descriptions:
        time.sleep(3)
        description = Create.query.get(id)
        descriptions = [description.sent2, description.sent2_2, description.sent2_3,
                        description.sent2_4, description.sent2_5, description.sent2_6,
                        description.sent2_7, description.sent2_8, description.sent2_9,
                        description.sent2_10, description.sent2_11, description.sent2_12,
                        description.sent2_13, description.sent2_14, description.sent2_15,
                        description.sent2_16, description.sent2_17, description.sent2_18,
                        description.sent2_19]

    
    print('edit_sent2 starting now')  

    print('sentences:')
    for sentence in descriptions:
        print(sentence)
    print()

    descriptions = remove_bad_sentences(descriptions)        
    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores/descriptions after edit:')
    for i, (desc, scr) in enumerate(zip(descriptions, scores)):
        print(int(scr), desc)

    # getting the description inputs
    title, cat, features = format_inputs(description)

    candidate1, descriptions, scores = pop_best_sentence(descriptions,
                                                        scores)
    print('candidate1:')
    print(candidate1)
    print('score:')
    print(score)
    candidate2, descriptions, scores = pop_best_sentence(descriptions,
                                                        scores)
    print('candidate2:')
    print(candidate2)
    print('score:')
    print(score)

    sent = return_most_similar(features,[candidate1, candidate2])[0]

    print('winner:')
    print(sent)

    update = Create.query.filter_by(id=id).update({'sent2_winner': sent})
    db.session.commit()
    print()
    print('edit_sent2 complete')
    print()
    return id


def edit_sent3(id):
    """
    Cull sent3 candidates and put best candidate back into database
    """
    # initialize model
    from transformers import OpenAIGPTTokenizer, OpenAIGPTLMHeadModel
    model = OpenAIGPTLMHeadModel.from_pretrained('perciapp/models/openai_gpt')
    model.eval()
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')

    # repeatedly pull candidates until all have been generated
    description = Create.query.get(id)
    descriptions = [description.sent3, description.sent3_2, description.sent3_3,
                        description.sent3_4, description.sent3_5, description.sent3_6,
                        description.sent3_7, description.sent3_8, description.sent3_9,
                        description.sent3_10, description.sent3_11, description.sent3_12,
                        description.sent3_13, description.sent3_14, description.sent3_15,
                        description.sent3_16, description.sent3_17, description.sent3_18,
                        description.sent3_19]

    while None in descriptions:
        time.sleep(3)
        description = Create.query.get(id)
        descriptions = [description.sent3, description.sent3_2, description.sent3_3,
                        description.sent3_4, description.sent3_5, description.sent3_6,
                        description.sent3_7, description.sent3_8, description.sent3_9,
                        description.sent3_10, description.sent3_11, description.sent3_12,
                        description.sent3_13, description.sent3_14, description.sent3_15,
                        description.sent3_16, description.sent3_17, description.sent3_18,
                        description.sent3_19]

    print('edit_sent3 starting now')

    print('sentences:')
    for sentence in descriptions:
        print(sentence)
    print()

    descriptions = remove_bad_sentences(descriptions)        
    scores = [score(i, tokenizer, model) for i in descriptions]

    print('scores/descriptions after edit:')
    for i, (desc, scr) in enumerate(zip(descriptions, scores)):
        print(int(scr), desc)

    # getting the description inputs
    title, cat, features = format_inputs(description)

    candidate1, descriptions, scores = pop_best_sentence(descriptions,
                                                        scores)
    print('candidate1:')
    print(candidate1)
    print('score:')
    print(score)
    candidate2, descriptions, scores = pop_best_sentence(descriptions,
                                                        scores)
    print('candidate2:')
    print(candidate2)
    print('score:')
    print(score)

    sent = return_most_similar(features,
                                    [candidate1, candidate2])[0]

    print('winner:')
    print(sent)

    update = Create.query.filter_by(id=id).update({'sent3_winner': sent})
    db.session.commit()

    description = Create.query.get(id)
    winners = [description.sent1_winner, description.sent2_winner]

    while None in winners:
        time.sleep(3)
        description = Create.query.get(id)
        winners = [description.sent1_winner, description.sent2_winner]

    final_output = period_check(description.sent1_winner) + period_check(description.sent2_winner) + period_check(description.sent3_winner)
    update = Create.query.filter_by(id=id).update({'description':final_output})
    db.session.commit()
    print()
    print('edit_sent3 complete')
    return id

def period_check(description):
    if description.endswith('.'):
        return description
    else:
        return description + '.'
