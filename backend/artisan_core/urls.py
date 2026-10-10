"""
URL Configuration for artisan_core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

urlpatterns = [
    # Frontend SPA
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # REST API endpoints
    path('api/v1/', include('artisans_app.urls')),
    
    # GraphQL Endpoint with GraphiQL Explorer
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True)), name='graphql'),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True)), name='graphql_slash'),
]
