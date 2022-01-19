from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from oslcapi.extensions import apispec
from oslcapi.api.resources import *
from oslcapi.api.schemas import UserSchema

blueprint = Blueprint("api", __name__, url_prefix="/service")
api = Api(blueprint)

'''

    ENDPOINTS DEFINITION

'''

# Service Providers Endpoints
api.add_resource(ServiceProvider, "/serviceProviders/<int:service_provider_id>", endpoint="service_provider_by_id")
api.add_resource(ServiceProviderCatalog, "/serviceProviders/catalog")

api.add_resource(OSLCResource, "/serviceProviders/<int:service_provider_id>/changeRequests/<int:oslc_resource_id>", endpoint="oslc_resource_by_service_provider_and_id")
api.add_resource(OSLCResourceList, "/serviceProviders/<int:service_provider_id>/changeRequests", endpoint="oslc_resource_by_service_provider")

api.add_resource(TrackedResourceSet, "/trackedResourceSet")
api.add_resource(TRSBase, "/baseResources")
api.add_resource(TRSChangeLog, "/changeLog/<int:change_log_id>", endpoint="change_log_by_id")

api.add_resource(EventReceived, "/event/payload")

@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400