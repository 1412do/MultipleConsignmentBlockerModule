import json
import datetime
from .RestService import RestServiceProvider
from .defaultEnums import *
from .CustomBlockerException import CustomBException


class MultipleConsignmentsBlockerService:
    def __init__(self):
        self._from_date = None
        self._to_date = None
        self._converted_date = None
        self._parameters = {}
        self._token = None
        self.rest_service_provider = None
        self._data = None
        self._headers = None

    @property
    def fromDate(self):
        return self._from_date

    @fromDate.setter
    def fromDate(self, date):
        self._from_date = date

    @property
    def toDate(self):
        return self._to_date

    @toDate.setter
    def toDate(self, date):
        self._to_date = date

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, t):
        self._token = t

    def convert_to_millis(self, date: datetime.datetime):
        self._converted_date = datetime.datetime.timestamp(date)
        return int(self._converted_date) * 1000

    def get_date_dict(self, date) -> dict:
        resp = {}
        final = date.split('-')
        resp.setdefault('year', int(final[0]))
        resp.setdefault('month', int(final[1]))
        resp.setdefault('day', int(final[2]))
        return resp

    def set_time_params_for_fetch(self):
        from_t_dict = self.get_date_dict(self.fromDate)
        to_t_dict = self.get_date_dict(self.toDate)
        from_date_time_from_dict = datetime.datetime(
            from_t_dict.get('year'),
            from_t_dict.get('month'),
            from_t_dict.get('day')
        )
        to_date_time_from_dict = datetime.datetime(
            to_t_dict.get('year'),
            to_t_dict.get('month'),
            to_t_dict.get('day')
        )
        self.fromDate = self.convert_to_millis(from_date_time_from_dict)
        self.toDate = self.convert_to_millis(to_date_time_from_dict)
        if self.fromDate > self.toDate:
            raise CustomBException("To Date cannot be bigger than from date, retry again.")
        else:
            self._parameters.setdefault('fromDateTime', self.fromDate)
            self._parameters.setdefault('toDateTime', self.toDate)

    def check_token(self):
        self.rest_service_provider = RestServiceProvider()
        request_args = RestFields.REST_FIELDS.value
        request_args.__setitem__('base_url', Urls.SSO_BASE.value)
        request_args.__setitem__('endpoint', Endpoints.CHECK_TOKEN.value)
        request_args.__setitem__('method', RestMethods.GET)
        request_args.__setitem__('params', {'token': self.token})
        response = self.rest_service_provider.executeRest(request_args)
        if not response or response.get('error'):
            raise CustomBException(
                "Invalid Token. Please provide a valid token. Error -> {}".format(response.get('error')))
        elif not response.get('active'):
            raise CustomBException(
                "User is inactive, stopping further execution."
            )
        return response

    def get_json(self, data):
        return json.loads(data)

    def fetch(self, reason_ids: list):
        self.rest_service_provider = RestServiceProvider()
        self._data = reason_ids
        self._headers = {'Authorization': 'Bearer {}'.format(self.token)}
        self.set_time_params_for_fetch()
        request_args = RestFields.REST_FIELDS.value
        request_args.__setitem__('base_url', Urls.ZOOM_API_BASE.value)
        request_args.__setitem__('endpoint', Endpoints.GET_BLOCKERS_BY_REASONS.value)
        request_args.__setitem__('method', RestMethods.POST)
        request_args.__setitem__('params', self._parameters)
        request_args.__setitem__('headers', self._headers)
        request_args.__setitem__('data', self._data)
        response = self.rest_service_provider.executeRest(request_args)
        return response

    def act(self, action: Actions, cnotes_id_list, reason: Reasons):
        self.rest_service_provider = RestServiceProvider()
        self._data = {
            'consignmentId': None,
            'reason': reason.value.get('reason'),
            'subReason': reason.value.get('subReason'),
            'requestType': action.value
        }
        self._headers = {'Authorization': 'Bearer {}'.format(self.token)}
        response_map = {}
        request_args = RestFields.REST_FIELDS.value
        request_args.__setitem__('base_url', Urls.ZOOM_API_BASE.value)
        request_args.__setitem__('endpoint', Endpoints.CONSIGNMENT_BLOCKER.value)
        request_args.__setitem__('method', RestMethods.POST)
        request_args.__setitem__('headers', self._headers)
        request_args.__setitem__('params', None)
        for i in cnotes_id_list:
            self._data.__setitem__('consignmentId', i)
            request_args.__setitem__('data', self._data)
            print("\nINFO: Prepared request->", request_args)
            resp = self.rest_service_provider.executeRest(request_args)
            response_map.setdefault(str(i), resp.get('status'))
        return response_map
