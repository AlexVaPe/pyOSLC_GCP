from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from oslcapi.extensions import apispec
from oslcapi.api.resources import *
from oslcapi.api.schemas import UserSchema


blueprint = Blueprint("api", __name__, url_prefix="/service")
api = Api(blueprint)


api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user_by_id")
api.add_resource(UserList, "/users", endpoint="users")


api.add_resource(ServiceProvider, "/serviceProviders/<int:service_provider_id>", endpoint="service_provider_by_id")
api.add_resource(ServiceProviderCatalog, "/serviceProviders/catalog")

# Directory Endpoints
api.add_resource(Directory_OSLCResource, "/serviceProviders/<int:service_provider_id>/directory/<int:oslc_resource_id>"
                 , endpoint="directory_oslc_resource_by_service_provider_and_id")
# Aquí van a mandarse los post para crear los recursos
api.add_resource(Directory_OSLCResourceList, "/serviceProviders/<int:service_provider_id>/directory"
                 , endpoint="directory_oslc_resource_by_service_provider")

# VM Endpoints
api.add_resource(VM_OSLCResource, "/serviceProviders/<int:service_provider_id>/instance/<int:oslc_resource_id>"
                 , endpoint="vm_oslc_resource_by_service_provider_and_id")
api.add_resource(VM_OSLCResourceList, "/serviceProviders/<int:service_provider_id>/instance"
                 , endpoint="vm_oslc_resource_by_service_provider")

# Cluster Endpoints
api.add_resource(Cluster_OSLCResource, "/serviceProviders/<int:service_provider_id>/cluster/<int:oslc_resource_id>"
                 , endpoint="cluster_oslc_resource_by_service_provider_and_id")
api.add_resource(Cluster_OSLCResourceList, "/serviceProviders/<int:service_provider_id>/cluster"
                 , endpoint="cluster_oslc_resource_by_service_provider")

# OSLC Actions
api.add_resource(OSLCAction, "/action", endpoint="oslc_action")

# TRS Endpoints
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
