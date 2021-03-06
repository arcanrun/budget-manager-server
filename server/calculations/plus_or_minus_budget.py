"""
Plus and Minus buttons for budget card
"""
import json
from django.http import JsonResponse
from ..models import Vkuser, History
import datetime


from ..helpers import is_comment_valid, clear_string, logger, is_valid_number, get_updated_data, make_calculations, make_calculations_full,  costsPattern, history_saver, next_pay_day, get_id_from_vk_params, is_user_registered

from ..auth.chcek_sign import is_valid, insert_client_sign, make_dict_from_query
from ..auth.check_origin import is_allowed_origin


def plus_or_minus_budget(request):
    # if not is_allowed_origin(request):
    #     return JsonResponse({
    #         'RESPONSE': 'BAD_REQUEST'
    #     })

    response = {'RESPONSE': 'AUTH_ERROR', 'PAYLOAD': {}}
    req = json.loads(str(request.body, encoding='utf-8'))
    logger('calc_budget:RECIVED', req)

    valid_opertaion_type = ['minus', 'plus']
    valid_type = ['budget']

    operation = req['operation']
    type = req['type']

    try:
        comment = clear_string(req['comment'])
        if not is_comment_valid(comment):
            return JsonResponse({
                'RESPONSE': 'BAD_REQUEST'
            })
    except:
        comment = False

    vk_id = get_id_from_vk_params(str(req['params']))
    query_params = make_dict_from_query(str(req['params']))
    client_secret = insert_client_sign()

    if is_valid(query=query_params, secret=client_secret) and operation in valid_opertaion_type and type in valid_type:

        if not is_valid_number(req['value']):
            response = {'RESPONSE': 'VALUE_ERROR', 'PAYLOAD': {}}
            return JsonResponse(response)

        value = round(float(req['value']), 2)
        date_now = datetime.datetime.now()

        all_users = Vkuser.objects.all()
        for field in all_users:
            if (vk_id == field.id_vk):
                budget = float(field.budget)
                if (operation == 'minus'):
                    budget -= value

                if (operation == 'plus'):
                    budget += value

                resArr = make_calculations_full(
                    field.common, field.fun, field.invest, field.days_to_payday, budget)
                Vkuser.objects.filter(id_vk=vk_id).update(
                    budget=budget, common=resArr[0], fun=resArr[1], invest=resArr[2])

                history_saver(field.id_vk, date_now,
                              operation, value, type, comment)
                break

        response = get_updated_data(vk_id)
        logger('calc_budget:RESPONSE', response)

        return JsonResponse(response)
    else:
        logger('calc_budget:RESPONSE', response)

        return JsonResponse(response)
