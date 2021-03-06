"""
Used for history page
"""
import json
from django.http import JsonResponse
import datetime
from datetime import timedelta
from ..models import Vkuser, History

from ..helpers import logger, get_updated_data, make_calculations, make_calculations_full,  costsPattern, history_saver, next_pay_day, get_id_from_vk_params, is_user_registered

from ..auth.chcek_sign import is_valid, insert_client_sign, make_dict_from_query


def get_short_history(request):
    response = {'RESPONSE': 'ERROR_AUTH', 'PAYLOAD': []}
    req = json.loads(str(request.body, encoding='utf-8'))
    logger('get_history_short:RECIVED', req)

    vk_id = get_id_from_vk_params(str(req['params']))
    query_params = make_dict_from_query(str(req['params']))
    client_secret = insert_client_sign()

    if is_valid(query=query_params, secret=client_secret):
        history = History.objects.all()
        user = Vkuser.objects.all()
        history_object = {}
        cost_object = {'operation': '', 'value': ''}
        timezone = ''

        for user_field in user:
            if (vk_id == user_field.id_vk):
                timezone = user_field.timezone
                break
        for field in history:
            if (vk_id == field.id_vk):
                with_time_zone = datetime.datetime.strptime(
                    field.date, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=timezone)
                foramated_date = with_time_zone.strftime('%Y-%m-%d')
                # foramated_date = datetime.datetime.strptime(
                #     foramated_date, '%Y-%m-%d')
                # foramated_date = foramated_date.strftime('%d.%m.%Y')
                if foramated_date in history_object:
                    cost_object['value'] = field.value
                    cost_object['operation'] = field.operation
                else:
                    history_object[foramated_date] = []

                    cost_object['value'] = field.value
                    cost_object['operation'] = field.operation

                history_object[foramated_date].append(cost_object)

                cost_object = {
                    'operation': '', 'value': ''}

        for k, v in history_object.items():
            v.reverse()
            response['PAYLOAD'].append({k: v})
        response['PAYLOAD'].reverse()
        response['RESPONSE'] = 'SUCCESS'

        logger('get_history_short:RESPONSE', response)

        return JsonResponse(response)

    else:
        logger('get_history:RESPONSE', response)

        return JsonResponse(response)
