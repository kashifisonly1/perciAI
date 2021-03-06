from transformers import GPT2LMHeadModel, GPT2Tokenizer
from flask import request

import torch
import torch.nn.functional as F
import numpy as np
import math
import re

import pandas as pd

MAX_LENGTH = int(10000)  # Hardcoded max length to avoid infinite loop

args = {}
args["model_type"] = 'gpt2'
args['temperature'] = 1.0
args['top_k'] = 0
args['top_p'] = 0.9
args['length'] = 45
args['no_cuda'] = True
args['padding_text'] = ''

def clean_up_sent(sent):
    '''
    returns a spell-checked, grammar-checked, length-checked and otherwise polished sentence
    '''
    if sent.endswith(("<eos>", "<eos", "<eo", "<e", "<")):
        sent = sent[:sent.rfind('<')]
    import language_tool_python
    tool = language_tool_python.LanguageTool('en-US')
    sent = tool.correct(sent)
    if len(sent) > 199:
        sent = sent[:198]
    return sent

def return_most_similar(first, secondlist):
    '''
    returns ordered list of secondlist, with most similar
    entries first and least similar entries last
    '''
    import spacy
    nlp = spacy.load("en_core_web_md")

    firstDoc = nlp(first)

    similarity = []

    for entry in secondlist:
        entryDoc = nlp(entry)
        similarity.append(firstDoc.similarity(entryDoc))

    similarity = pd.Series(similarity, index=secondlist)
    similarity.sort_values(ascending=False, inplace=True)

    return list(similarity.index)


def pop_best_sentence(sent_list, score_list):

    index = np.argmin(score_list, axis=0)
    candidate1 = sent_list[index]
    sent_list.remove(candidate1)
    score_list.remove(score_list[index])
    return candidate1, sent_list, score_list


def score(sentence, tokenizer, model):
    if sentence == np.NaN:
        return 1e4
    tokenize_input = tokenizer.tokenize(sentence)
    tensor_input = torch.tensor([tokenizer.convert_tokens_to_ids(tokenize_input)])
    loss = model(tensor_input, labels=tensor_input)
    return math.exp(loss[0])


def brand_remove(description, model):
    '''
    Removes the brand from a model-generated sentence.
    '''
    try:
        first, second = re.split('(?i)' + model, description)
    except:
        print('split error:')
        print(str(len(re.split(model, description))))
        print(description)
        return description

    if second.strip().startswith('from ') or second.strip().startswith('by '):
        delimiters = ['.', ' is ', ' takes ', ' gives ', ' makes ',
                      ' creates ', ' features ', ' will ', ' crafted ',
                      ' a ',' has ', ' for', ' to', ' with', ' are', ' isnt', "isn't"]
        low = 100
        for item in delimiters:
            place = second.find(item)
            if 0 < place < low:
                low = place
        result = first + model + second[low:]
        return result
    

    elif first.strip().endswith("'s"):
        result = first.strip().rsplit(' ', 1)[0] + ' ' + model + second
        return result

    else:
        return description


def format_inputs(description):
    title = description.title
    gender = description.gender
    category = description.category
    subcategory = description.subcategory
    detail1 = description.detail1
    detail2 = description.detail2
    detail3 = description.detail3
    detail4 = description.detail4
    detail5 = description.detail5

    # concatenating the category item
    cat = gender + '/' + category + '/' + subcategory

    # concatenating details into features list
    features = []
    for detail in [detail1, detail2, detail3, detail4, detail5]:
        if len(detail) > 1:
            features.append(detail)

    features = ' - '.join(features)

    return title, cat, features


def set_seed(args):
    np.random.seed(args['seed'])
    torch.manual_seed(args['seed'])
    if args['n_gpu'] > 0:
        torch.cuda.manual_seed_all(args['seed'])


def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    """ 
    Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
        Args:
            logits: logits distribution shape (batch size x vocabulary size)
            top_k > 0: keep only top k tokens with highest probability (top-k filtering).
            top_p > 0.0: keep the top tokens with
            cumulative probability >= top_p (nucleus filtering).
            Nucleus filtering is described in Holtzman et al.
            (http://arxiv.org/abs/1904.09751)
        From: https://gist.github.com/thomwolf/1a5a29f6962089e871b94cbd09daf317
    """
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        # scatter sorted tensors to original indexing
        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits


def sample_sequence(model, length, context, num_samples=1, 
                    temperature=1, top_k=0, top_p=0.9, is_xlnet=False, 
                    repetition_penalty=1.0, device='cpu'):
    context = torch.tensor(context, dtype=torch.long, device=device)
    context = context.unsqueeze(0).repeat(num_samples, 1)
    generated = context
    with torch.no_grad():
        for _ in range(length):

            inputs = {'input_ids': generated}

            outputs = model(**inputs)
            next_token_logits = outputs[0][0, -1, :] / (temperature if temperature > 0 else 1.)

            filtered_logits = top_k_top_p_filtering(next_token_logits,
                                                    top_k=top_k,
                                                    top_p=top_p)
            next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1),
                                           num_samples=num_samples,
                                           replacement=True)
            generated = torch.cat((generated, next_token.unsqueeze(1)), dim=1)
    return generated


def generate(args):

    args['device'] = torch.device("cuda" if torch.cuda.is_available() and not args['no_cuda'] else "cpu")
    args['n_gpu'] = torch.cuda.device_count()

    set_seed(args)

    args['model_type'] = args['model_type'].lower()
    model_class, tokenizer_class = GPT2LMHeadModel, GPT2Tokenizer
    tokenizer = tokenizer_class.from_pretrained('gpt2')
    model = model_class.from_pretrained(args['model_name_or_path'])
    model.to(args['device'])
    model.eval()

    if args['length'] < 0 and model.config.max_position_embeddings > 0:
        args['length'] = model.config.max_position_embeddings
    elif 0 < model.config.max_position_embeddings < args['length']:
        # No generation bigger than model size 
        args['length'] = model.config.max_position_embeddings
    elif args['length'] < 0:
        # avoid infinite loop
        args['length'] = MAX_LENGTH 

    while True:
        raw_text = args['prompt'] if args['prompt'] else input("Model prompt >>> ")

        if args['model_type'] in ["transfo-xl", "xlnet"]:
            # Models with memory likes to have a long prompt for short inputs.
            raw_text = (args['padding_text']) + raw_text
        context_tokens = tokenizer.encode(raw_text, add_special_tokens=False)
        outputs = sample_sequence(
            model=model,
            context=context_tokens,
            length=args['length'],
            temperature=args['temperature'],
            top_k=args['top_k'],
            top_p=args['top_p'],
            device=args['device']
        )
        outputs = outputs[:, len(context_tokens):].tolist()
        text_candidates = []
        for out in outputs:
            text = tokenizer.decode(out,
                                    clean_up_tokenization_spaces=False,
                                    skip_special_tokens=False)
            text = text[: text.find('<eos>')]
            text_candidates.append(text)
        if args['prompt']:
            break
    del model
    return text_candidates
